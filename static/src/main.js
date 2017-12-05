// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
/* eslint-disable no-new */
import Vue from 'vue';
import router from './router';
import header from './components/layout/header.vue';
import right from './components/layout/right.vue';
import left from './components/layout/left.vue';
import loginWindow from './components/layout/login.vue';
import registerWindow from './components/layout/register.vue';

import './static/legoland.css';
import './static/layout.css';
import './static/AdminLTE/AdminLTE.css';
import './static/AdminLTE/skins/_all-skins.css';
import './static/bootstrap/css/bootstrap.css';
import './static/font-ion/ionicons.css';
import './static/font-awesome/css/font-awesome.css';

import { Overlay,Mask,Toast } from 'vpui';
import VueCookies from 'vue-cookies';
Vue.use(VueCookies);
new Vue({
    el: '#J-app',
    router,
    data(){
        return{
            miniAside: false,
            showApp: false,
        }
    },
    template: '<div id="app" class="dns-app">'+
                    '<div v-if="showApp" style="width:100%">'+
                        '<dns-header  @aside:toogle="asideToogle()"></dns-header>'+
                        '<left ref="aside" class="sidebar"></left>'+
                        '<right ref="rightContent">'+
                            '<keep-alive>'+
                                '<router-view></router-view>'+
                            '</keep-alive>'+
                        '</right>'+
                    '</div>'+
                    '<login-window ref="loginWindow" @loginSuccess="loginSuccess"></login-window>'+
                    '<register-window ref="registerWindow"></register-window>'+
              '</div>',
    components: {
        left: left,
        right: right,
        dnsHeader: header,
        vpLogin: Overlay,
        vpMask: Mask,
        loginWindow: loginWindow,
        registerWindow: registerWindow

    },

    methods: {
        asideToogle(){
            this.miniAside = !this.miniAside;
            this.$refs.aside.miniAside(this.miniAside);
            this.$refs.rightContent.miniAside(this.miniAside);
        },
        loginSuccess(){
            this.showApp = true;
        },
        operateLeft(){
            this.$refs.aside.dosomething();
        },
        resetSidebar () {
            this.$refs.aside.initSidebar();
        },
    },

    mounted(){

        //Toast.loading('ssss', false,10000000);
        //this.$refs.loginMask.show();
        let token = this.$cookies.get('dns-cookie-token');
        if(token){
            this.$refs.loginWindow.hide();
            this.showApp = true;
        }else{
            this.$refs.loginWindow.show();
        }

    }
});
