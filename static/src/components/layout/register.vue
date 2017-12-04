<template>
    <div>
        <vp-mask ref="registerMask" :visible="isShow">
            <div class="register-background">
                <div class="project-name">DNS管理平台</div>
            </div>
        </vp-mask>
        <overlay class="register-window" :visible="isShow" refs="registerWindow">
            <div class="register-content">
                <h1>新用户注册</h1>
                <input v-valid="{required:true}" group="newUser" class="register-input" placeholder="请输入本地用户名" v-model="username">
                <input v-valid="{required:true}" group="newUser" class="register-input" placeholder="请输入密码" type="password" v-model="password">
                <input v-valid="{required:true}" group="newUser" class="register-input" placeholder="确认密码" type="password" v-model="password2">
                <input v-valid="{required:true, email: true}" group="newUser" class="register-input" placeholder="邮箱" type="text" v-model="email">
                <button class="register-btn" @click="register">注册</button>
            </div>
        </overlay>
    </div>
</template>
<script>
    import {Overlay, Mask, Toast, Alert, Valid} from 'vpui';
    import _ from '../../components/fn/tool';
    import Ajax from 'ajax';
    let registerAjax = new Ajax();
    export default {
        data(){
            return {
                isShow: false,
                username: '',
                password: '',
                password2 : '',
                email : '',
            }
        },
        directives: {
            "valid":Valid,
        },
        components: {
            overlay: Overlay,
            vpMask: Mask,
            Alert : Alert
        },
        mounted(){
            let self = this;
            /*setTimeout(function(){
                self.$refs.userNameInput.focus();
            });*/
        },
        methods: {
            validRegister () {
                let errLen = this.$vform['newUser'].checkAll().length;
                this.$vform['newUser'].checkAll();
                // !errLen && Toast.success('验证通过，发送请求', true);
                return !errLen;
            },
            show(){
                this.isShow = true;
            },
            hide(){
                this.isShow = false;
            },
            register (nub){
                if (this.password.length < 6 || this.password2.length < 6) {
                    Alert('密码必须大于6位！');
                    return;
                }
                if (this.password !== this.password2) {
                    Alert('您输入的2次密码不相同！');
                    return;
                }
                if (!this.validRegister()) return;
                
                let url = 'http://hfdns-test.ipo.com/auth/login_local';
                let self = this;
                var data = {
                    "username": self.username,
                    "password": self.password,
                    "password2": self.password2, 
                    "email": self.email
                }
                
                Toast.loading('注册中...');
                _.trim(data);
                registerAjax.post({
                    url : url,
                    data : data,
                    success: function(response){
                        Toast.success('注册成功！');
                        self.isShow = false;
                        self.$parent.$refs.loginWindow.show();
                    }
                });
            },
        }
    }
</script>
<style>
    .register-title{
        text-align: center;
        font-size: 18px;
    }

    .register-window{
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

    .register-content{
        padding-top: 20px;
        background-color: #fff;
        height: 290px;
        border-radius: 3px;
        border-top-left-radius: 0;
    }
    

    .register-content .register-input,.register-password-helper{
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


    .register-password-helper{
        height: auto;
        padding: 0;
        border: 0;
        background: transparent;
        text-align: left;
        font-weight: normal;
    }

    .register-password-helper input[type="checkbox"]{
        display: inline-block;
        vertical-align: middle;
        margin: 0;
        margin-right: 10px;
    }


    .register-password-helper label{
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
    .register-background{
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
    .register-btn{
        width: 306px;
        height: 40px;
        background-color: #72BFF0;
        color:#fff;
        border: 0;
        margin:0 auto;
        display:block;
    }
    .register-title-item{
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
    h1{
        padding:0;margin:0 auto;
        font-size:18px;
        margin-bottom:10px;
        text-align:center;
        width:305px;

    }
    .lg-error-msg{
        width:305px;
        margin:auto;
        display:block;
    }
</style>