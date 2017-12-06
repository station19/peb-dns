import axios from 'axios';
import {Toast, Alert} from 'vpui';
import 'vue-cookies';
let NODE_ENV = process.env.NODE_ENV;
let baseURL = '//localhost:3001/';
if(NODE_ENV == 'production'){
    baseURL = '//hfdns-test.ipo.com/';
    //http://hfdns-test.ipo.com/auth/login_ldap
}
//const baseURL = '//hfdns-test.ipo.com/';


let instance = axios.create({
    baseURL,
    timeout: 10000,
    withCredentials: true
});

instance.interceptors.request.use(
    config => {
        let token = window.$cookies.get('dns-cookie-token');
        if(token) {
            config.headers.Authorization = `${token}`;
        }
        return config;
    },
    err => {
        console.log('reuest error');
    }
);

// http response 拦截器
instance.interceptors.response.use(
    response => {
        switch (response.data.code) {
            case 100000 :
                return response.data;
            break;
            case 100001 :
                Alert(response.data.msg);
            break;
            case 105000 :
                Alert(response.data.msg);
            break;
            default:
            break;
        }
    },
    error => {console.log(error.response)
        if (error.response) {
            let msg = '';
            switch (error.response.status) {
            case 401:
                Toast.error('登录失败');
                break;
            case 400:
                msg = error.response.data.message;

                if(typeof msg == 'object'){
                    let errorMsg = JSON.stringify(msg);
                    Alert(errorMsg);
                } else if(typeof msg == 'string'){
                    let errorMsg = msg;
                    let errorMsgDetail = error.response.data.error;
                    if(errorMsgDetail){
                        errorMsg += ": " +errorMsgDetail;
                    }
                    Alert(errorMsg);
                }
                break;
            case 403:
                msg = error.response.data.message;
                var code = error.response.data.code;
                if(code == 40301){
                    window.$cookies.set('dns-cookie-token', '');
                    window.$cookies.set('dns-cookie-username', '');
                    setTimeout(function(){
                        window.location.href = '/';
                    }, 1000);
                }
                Toast.error(msg);
                break;
            default:
                break;
            }
            

        }
        
    }
);



function ajax() {
    let authToken =  window.$cookies.get('dns-cookie-token');
    let config = {
        header: {
            'authorization': authToken
        }
    };
    this.post = function(options){
        this.showLoading(options);
        let self = this;
        instance.post(options.url,options.data, config)
            .then((response) => {
                self.handleSuccess(response,options);
            })
    }

    this.get = function (options) {
        this.showLoading(options);
        let self = this;
        instance.get(options.url, {params:options.data}, config)
            .then((response) => {
                self.handleSuccess(response,options);
            })
    }

    this.put = (options) => {
        this.showLoading(options);
        let self = this;
        instance.put(options.url,options.data, config)
            .then((response) => {
                self.handleSuccess(response,options);
            })
    }


    this.delete = (options) => {
        this.showLoading(options);
        let self = this;
        instance.delete(options.url,options.data, config)
            .then((response) => {
                self.handleSuccess(response,options);
            })
    }

    this.showLoading = (options) => {
        if(typeof options.showLoading == 'undefined' || options.showLoading){
            Toast.loading(options.loadingMsg || '请求中...', false, 3000);
        }
    }

    this.handleSuccess = (response, options) => {
        if(typeof response != 'undefined'){
            Toast.destroy();
            options.success(response);
        }
    }
}

export default ajax;
