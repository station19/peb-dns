<template>
    <div>
        <vp-mask ref="loginMask" :visible="isShow">
            <div class="login-background">
                <div class="project-name">DNS管理平台</div>
            </div>
        </vp-mask>
        <overlay class="login-window" :visible="isShow" refs="loginWindow">
            <vp-tabs @changed="tabChange">
                <vp-tab name="LDAP用户"></vp-tab>
                <vp-tab name="本地用户"></vp-tab>
            </vp-tabs>
            <div class="login-content">
                <form>
                    <input class="login-input" :placeholder="userNamePlaceHolder" v-model="username" ref="userNameInput" @keydown="inputKeyDown"></input>
                    <input class="login-input" placeholder="请输入密码" type="password" v-model="password" ref="passwordInput" @keydown="inputKeyDown"></input>
                    <button @click="login" class="login-btn">登录</button>
                    <!-- <div style="text-align:left;margin:0 10px 0 20px;float:left;">
                        <label><vp-checkbox />记住密码</label>
                    </div> -->
                    <div style="text-align:left;float:right;margin:6px 20px 0 20px;" v-if="isLocal"><a @click="newUser">新用户注册</a></div>
                    <div class="error-msg" v-cloak>{{errorMsg}}</div>
                </form>
            </div>
        </overlay>
    </div>
</template>
<script>
    import {Overlay, Mask, Toast, Tabs, Tab, Checkbox} from 'vpui';
    import Ajax from 'ajax';
    let loginAjax = new Ajax();
    export default {
        data(){
            return {
                isShow: false,
                isLocal: false,
                username: '',
                password: '',
                userMessage : '',
                userNamePlaceHolder: '请输入本地用户名',
                errorMsg: '',
            }
        },
        components: {
            overlay: Overlay,
            vpMask: Mask,
            'vp-tabs': Tabs,
            'vp-tab': Tab,
            'vp-checkbox': Checkbox
        },
        mounted(){
            let self = this;
            /*setTimeout(function(){
                self.$refs.userNameInput.focus();
            });*/
        },
        methods: {
            // 记住密码
            rememberPassword (e) {
                console.log(e.target.checked)
            },
            // 新用户注册页面
            newUser () {
                this.$parent.$refs.loginWindow.hide();
                this.$parent.$refs.registerWindow.show();
            },
            show(){
                this.isShow = true;
            },
            hide(){
                this.isShow = false;
            },
            login(){
                let self = this;
                self.errorMsg = '';
                let url = 'http://hfdns-test.ipo.com/auth/login_ldap';
                if (self.isLocal) {
                    url = 'http://hfdns-test.ipo.com/auth/login_local';
                }
                if(self.username.length == 0 || self.password.length == 0){
                    self.errorMsg = '用户名 或 密码不能为空！';
                    return;
                }

                let token = ''
                Toast.loading('登录中...')
                
                loginAjax.post(
                    {
                        url,
                        data: {
                            username: self.username,
                            password: self.password
                        },
                        //username: 'LIJIAJIA873',
                        //password: 'LIjia,216559'
                        success: function(response){
                            Toast.success('登录成功！');
                            token = response.data.token;
                            if(token && token.length > 0){
                                self.isShow = false;
                                self.$cookies.set('dns-cookie-token',token);
                                self.$cookies.set('dns-cookie-username', response.data.user_info.username);
                                localStorage.user_info = JSON.stringify(response.data.user_info);
                                self.$emit('loginSuccess');
                            }
                        }
                    }
                )
            },
            inputKeyDown(event){
                let inputType = event.target.getAttribute('type');
                if(event.keyCode == 13){
                    if(inputType && inputType == 'password'){
                        this.login();
                    }else{
                        this.$refs.passwordInput.focus();
                    }
                }
            },
            tabChange(obj){
                /*this.username = '';
                this.password = '';*/
                let index = obj.index;
                this.errorMsg = '';
                if(index == 1){
                    this.isLocal = true;
                    this.userNamePlaceHolder = '请输入本地用户名';
                }else{
                    this.isLocal = false;
                    this.userNamePlaceHolder = '请输入LDAP用户名';
                }
            }
        }
    }
</script>
<style scoped>
label{
    color:#333;
}
    .error-msg{
        color: red;
        font-size: 14px;
        font-style: italic;
        margin-top: 10px;
        margin-left: 20px;
        text-align: left;
    }

    .login-title{
        text-align: center;
        font-size: 18px;
    }

    .login-window{
        width: 346px;
        /*height: 284px;*/
        height: 384px;
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        right: 0;
        margin: auto;
        border-radius: 10px;
    }

    .login-content{
        padding-top: 40px;
        text-align: center;
        background-color: #fff;
        height: 235px;
        border-radius: 3px;
        border-top-left-radius: 0;
    }
    

    .login-input,.login-password-helper{
        display: block;
        width: 305px;
        height: 36px;
        margin: 0 auto;
        margin-bottom: 8px;
        background: #F5FAFE;
        border: 1px solid #72BFF0;
        border-radius: 4px;
        padding: 3px;
        padding: 12px 35px 12px 12px;
        color: #69B8EA;
    }   


    .login-password-helper{
        height: auto;
        padding: 0;
        border: 0;
        background: transparent;
        text-align: left;
        font-weight: normal;
    }

    .login-password-helper input[type="checkbox"]{
        display: inline-block;
        vertical-align: middle;
        margin: 0;
        margin-right: 10px;
    }


    .login-password-helper label{
        font-weight: normal;
        line-height: 24px;
        height: 24px;
        font-size: 12px;
    }

    .find-paddword{
        float: right;
    }
    
    .input-label{
        display:inline-block;
        width: 80px;
        text-align: right;
    }
    .login-background{
        background-color: #72BFF0;
        height: 100%;
        background-image: url('./images/dns128x128.png');
        background-repeat: no-repeat;
        background-size: auto 1200px;
        background-position: -400px -400px;
        opacity: 1;
    }
    .project-name{
        position: absolute;
        top: 20px;
        right: 30px;
        opacity: 0.9;
        font-family: PingFangSC-Medium;
        font-size: 30px;
        color: #FFFFFF;
    }
    .login-btn{
        width: 306px;
        height: 40px;
        background-color: #72BFF0;
        color:#fff;
        border: 0;
    }
    .login-title-item{
        background-color: #fff;
        height: 50px;
        line-height: 50px;
       /* width: 160px;*/
        color: #72BFF0;
        border-top-left-radius: 3px;
        border-top-right-radius: 3px;
    }
    .project-name{
        background: url('./images/dns.png') no-repeat;
        padding-left:50px;
        background-size: auto 41px;
    }
</style>