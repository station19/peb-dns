<template>
    <header :class="['main-header', miniAsideClass]">
        <a href="#/" class="logo" @click="clickHead">
            <span class="dns-log">
                <b>HF</b>
                DNS
            </span>
            <span class="dns-log-mini">
                <b>D</b>NS
            </span>
        </a>
        <nav class="navbar navbar-static-top">
            <a class="arrow" href="javascript:;" @click="toogleAside()">
                <i class="ion-android-menu"/>
            </a>
            <div class="navbar-custom-menu">
                <picker class="custom-picker">
                    <div class="user-info"><img class="header-pic" src="./images/boxed-bg.jpg"></img><span class="user-name">{{username}}</span></div>
                    <div slot="picker-content" class="user-panel">
                        <div><a href="#/dns/userConfig">用户信息</a></div>
                        <div><a href="javascript:;" @click="logOut">退出</a></div>
                    </div>
                </picker>
            </div>
        </nav>
    </header>
</template>
<script>
    import {Picker} from 'vpui';
    export default {
        data(){
            return {
                name: '222',
                miniAsideClass: '',
                username:'',
                sib : true
            }
        },
        components: {
            picker: Picker
        },
        methods:{
            toogleAside(){
                this.$emit('aside:toogle');
                this.miniAsideClass = this.miniAsideClass == 'main-header-miniaside' ? '' : 'main-header-miniaside';
            },
            logOut(){
                this.$cookies.remove('dns-cookie-token');
                window.location.href = '/';
            },
            clickHead () {
                this.$parent.operateLeft();
            }
        },
        mounted(){
            this.username = this.$cookies.get('dns-cookie-username');
        }
    }

</script>
<style scoped>
    .main-header{
        position: fixed;
        width: 100%;
    }
    
    .navbar{
        background-color: #3c8dbc;
        min-height: 51px;
    }
    
    .arrow{
        color: #748393;
        line-height: 50px;
        font-size: 20px;
        height: 50px;
        display: block;
        width: 50px;
        text-align: center;
        text-decoration: none;
        float: left;
    }

    .arrow:hover{
        background-color: #367fa9;
    }

    .user-name{
        color: #748393;
    }

    .logo{
        text-decoration: none;
    }
    .main-header-miniaside .logo{
        width: 50px;
        padding: 0 2px;
    }

    .main-header .dns-log{
        display: block;
    }

    .main-header .dns-log-mini{
        display: none;
    }


    .main-header-miniaside .navbar{
        margin-left: 50px;
    }
    .main-header-miniaside .dns-log{
        display: none;
    }
    .main-header-miniaside .dns-log-mini{
        display: block;
    }
    
    .user-info{
        height: 50px;
        line-height: 50px;
        padding-left: 50px;
        padding-right: 20px;
    }
    
    .custom-picker{
        margin-right: 15px;
    }
    .header-pic{
        width: 30px;
        height: 30px;
        border-radius: 50%;
        position: absolute;
        top: 50%;
        left: 10px;
        transform: translateY(-50%);
    }

    .user-panel{
        width: 150px;
        background-color: #fff;
    }

    .user-panel a {
        color: #748393;
    }
</style>
<style>
    body .vp-picker-rel{
        color: #fff;
        border: 0;
        cursor: pointer;
    }
</style>