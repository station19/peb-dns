<template>
    <div class="userConfig">
        <div class="inputData" v-for="(val, key, index) in usersMessage">
            <label v-if="key != '角色信息'">{{key}}</label>
            <input type="text" v-model="val.value" v-if="key != '角色信息'" :disabled="val.disabled">
        </div>
        <btn size="small" @click="saveData">保存</btn>
    </div>
</template>
<script>
import Ajax from 'ajax';
import { Button, Alert, Toast } from 'vpui';
import _ from '../components/fn/tool';

var dnsAjax = new Ajax();
var kv = {
    id : 'id',
    "username": "用户名",
    "roles": '角色信息',
    "role": '角色',
    "last_seen": "最后一次登录",
    "position": '职位',
    "location": '地址',
    "chinese_name": '中文名',
    "email": '邮箱',
    "member_since": "首次登录",
    "cellphone": '电话',
}

export default {
    data () {
        return {
            // 用户信息
            usersMessage : '',
        };
    },
    components:{
        btn: Button,
        Alert : Alert,
    },
    mounted(){
        sInit(this);
    },
    methods : {
        saveData () {
            userSave(this);
        }
    }
}


/*
    状态
*/
// 初始状态
var sInit = function (that) {
    getUserMessage(that);
};

// ajax
// 获取用户信息
var getUserMessage = function (that, data) {
    dnsAjax.get({
        url : 'http://hfdns-test.ipo.com/admin/users?username=' + that.$cookies.get('dns-cookie-username'),
        success (response) {
            var user = response.data.users[0];
            user.role = '';
            user.roles.forEach((item, index, arr) => {
                user.role += item.name + ', ';
            });
            that.usersMessage = _.paraKey(_.wrap(user, {
                id : {
                    disabled : 'disabled'
                },
                'last_seen' : {
                    disabled : 'disabled'
                },
                'member_since' : {
                    disabled : 'disabled'
                },
                role : {
                    disabled : 'disabled'
                },
                username : {
                    disabled : 'disabled'
                }
            }), _.invert(kv));
        }
    });
};
// 保存用户信息
var userSave = function (that) {
    dnsAjax.put({
        url : 'http://hfdns-test.ipo.com/admin/users/' + that.usersMessage.id.value,
        data : _.wrapBack(_.paraKey(that.usersMessage, kv)),
        success (response) {
            Toast.success('修改成功');
        }
    });
};


</script>
<style scoped lang="less">
    .userConfig{
        background-color:#fff;
        padding:20px;
    }
    .inputData{
        margin-bottom:10px;
    }
    label{
        color:#333;
        width:150px;
    }
    input{
        width:200px;
    }
</style>