<template>
    <div id='admin' class="admin-block">
        <h1 style="background-color:Turquoise;">用户</h1>
        <div class="grid-search-form">
            <input
                class="search-item"
                type="text" 
                :placeholder="value.name" 
                v-model="searchUserData[key].value" 
                v-for="(value, key, index) in searchUserData">
            </input>
            <btn  @click="searchUser">搜索</btn>
            <btn @click="resetForm">重置</btn>
        </div>
        <vp-grid :head="tableUser.col" :data="tableUserData" :colspan="tableUser.colspan">
            <div :slot="'cell:option_'+i" v-for="(item,i) in tableUserData">
                <btn size="small" @click="userEdit(item.id, i)">编辑</btn>
            </div>
        </vp-grid>
        <vp-mnpager :show-short-cut="true" ref="userPagination" v-on:to="userPageTo" style="float: left"></vp-mnpager>
        <!-- 编辑用户 -->
        <vp-dialog ref="editDialogUser" title="编辑用户" @dialog:save="modifyUser">
            <div class="clearfix">
                <div class="user-info clearfix">
                    <div class="form-group">
                        <label>id</label>
                        <input disabled type="text" class="form-control" v-model="editUserVal.id" group="editUser" v-valid="{required:true}">
                    </div>
                    <div class="form-group">
                        <label>用户名</label>
                        <input disabled type="text" class="form-control" v-model="editUserVal.username" group="editUser" v-valid="{required:true}">
                    </div>
                    <div class="form-group">
                        <label>中文名称</label>
                        <input type="text" class="form-control" v-model="editUserVal.chinese_name">
                    </div>
                    <div class="form-group">
                        <label>电话</label>
                        <input type="text" class="form-control" v-model="editUserVal.cellphone">
                    </div>
                    <div class="form-group">
                        <label>地址</label>
                        <input type="text" class="form-control" v-model="editUserVal.location">
                    </div>
                    <div class="form-group">
                        <label>职位</label>
                        <input type="text" class="form-control" v-model="editUserVal.position">
                    </div>
                    <div class="form-group">
                        <label>邮箱</label>
                        <input type="text" class="form-control" v-model="editUserVal.email">
                    </div>
                    <div class="form-group">
                        <label>首次登录时间</label>
                        <input disabled type="text" class="form-control" v-model="editUserVal.member_since" group="editUser" v-valid="{required:true}">
                    </div>
                    <div class="form-group">
                        <label>最近登录时间</label>
                        <input disabled type="text" class="form-control" v-model="editUserVal.last_seen" group="editUser" v-valid="{required:true}">
                    </div>
                    <div class="form-group">
                        <label>关联角色名称</label>
                        <textarea disabled class="form-control" name="" id="" cols="30" rows="10" v-model="editUserVal.roleName"></textarea>
                    </div>
                </div>
                <div class="user-role">
                    <div class="search-bar">
                        <input 
                            type="text" 
                            :placeholder="value.name" 
                            v-model="searchRoleData[key].value" 
                            v-for="(value, key, index) in searchRoleData" 
                            :style="'width:'+ ((value.name == 'id') ? '62px; margin-left:0px;' : '115px;')"
                        >
                        </input>
                        <btn @click="searchRole" style="margin-right:5px;">搜索</btn><btn @click="resetRoleForm">重置</btn>
                    </div>
                    <vp-grid :head="tableRole.col" :data="tableRoleData" :colspan="3" style="margin-bottom: 22px;">
                        <div :slot="'cell:option_'+i" v-for="(item,i) in tableRoleData">
                            <btn :type="item.isDanger" size="small" @click="relation(item.id, item)">
                                <template v-if="item.isDanger">取消关联</template>
                                <template v-else>关联用户</template>
                            </btn>
                        </div>
                    </vp-grid>
                    <vp-mnpager :show-short-cut="true" ref="rolePagination" v-on:to="rolePageTo" style="float: left"></vp-mnpager>
                </div>
            </div>
        </vp-dialog>
    </div>
</template>
<script>
import dialog from '../_complex/dialog.vue';
import { pageNub } from './methods';
import {Datagrid, Pager, Select, Button, Toast, Valid, Radio, Checkbox, Alert, MiniPager} from 'vpui';
import Ajax from 'ajax';
import _ from '../../components/fn/tool';
import dnsData from '../dnsData';

var dnsAjax = new Ajax();
var userManageData = dnsData('userManage');
var userManageDataUrl = dnsData('url');

export default {
    data () {
        return {
            nowEditId : '',
            // 用户表头
            tableUser: userManageData.tableUser,
            // 用户表体
            tableUserData: [],
            // 用户搜索框
            searchUserData: sReset(userManageData.searchUserDataEmpty),
            // 编辑的单个用户
            editUserVal: sReset(userManageData.editUserVal),
            // 角色搜索框
            searchRoleData: sReset(userManageData.searchRoleDataEmpty),
            // 角色表体
            tableRoleData: [],
            // 角色表头
            tableRole: userManageData.tableRole,
        }
    },
    components:{
        vpSelect : Select,
        vpGrid: Datagrid,
        vpDialog: dialog,
        vpPager: Pager,
        btn: Button,
        Alert : Alert,
        vpMnpager: MiniPager,
    },
    mounted(){
        sInit(this);
    },
    directives: {
        "valid":Valid,
    },
    methods: {
        // 重置用户搜索框
        resetForm(){
            this.searchUserData = sReset(userManageData.searchUserDataEmpty);
        },
        // 重置角色搜索框
        resetRoleForm(){
            this.searchRoleData = sReset(userManageData.searchRoleDataEmpty);
        },
        // 编辑用户
        userEdit (id, index) {
            sEdit(this, {
                isEditActive : [id],
                isEditLogic : [index]
            });
        },
        // 保存编辑
        modifyUser (id, index) {
            editSave(this);
        },
        // 角色分页
        rolePageTo (index){
            this.searchData('searchRoleData', index);
        },
        // 用户分页
        userPageTo (index){
            getUserTableList(this, {
                currentPage : index
            });
        },
        // 用户搜索
        searchUser () {
            getUserTableList(this, req(this.searchUserData));
        },
        // 权限搜索
        searchRole () {
            getRoleTableList(this, req(this.searchRoleData));
        },
        // 关联
        relation (id, item) {
            relationOperation(this, id, item);
        },
    }
}



/*
    状态
*/
// 编辑用户的当前状态
var sEdit = _.decorate(function isEditActive (id) {
    // 当前id
    this.nowEditId = id;
});
// 编辑用户的关联状态
var sRelation = _.decorate(function isRelationActive () {
    // 显示关联角色按钮状态
    if (!this.editUserVal.role) return;
    var arr = JSON.parse('[' + this.editUserVal.role + ']');
    for (let key in this.tableRoleData) {
        arr.indexOf(this.tableRoleData[key].id) != -1 ? this.tableRoleData[key].isDanger = 'danger' : this.tableRoleData[key].isDanger = '';
    }
}, false);
// 编辑用户的关联状态操作
var sRelationState = function (bl) {
    var o = function () {
        this.isDanger = '';
    };
    var t = function () {
        this.isDanger = 'danger';
    };
    var arr = bl ? [o, t] : [t, o];
    return (function () {
        return _.state.apply(null, arr);
    })();
};

// 初始状态
var sInit = function (that) {
    getUserTableList(that);
    // 编辑user
    sEdit.add(function isEditLogic (index) {
        this.$refs.editDialogUser.show();
        this.$vform['editUser'].resetStyle();
        this.editUserVal = _.clone(this.tableUserData[index]);
        // 过滤null
        for (var key in this.editUserVal) if (this.editUserVal[key] === null) this.editUserVal[key] = '';
        getRoleTableList(this);
    });
    // 编辑user的table
    sRelation.add(function isRelationLogic (response) {
        if (!response.data.roles) return;
        // 添加isDanger
        response.data.roles.forEach(function (item, index, arr) {
            item.isDanger = '';
        });
        this.tableRoleData = response.data.roles;
        this.$refs.rolePagination.setPage(pageNub(response.data.total), response.data.current_page);
    });
};

// 重置状态
var sReset = function (data) {
    return JSON.parse(JSON.stringify(data));
};

// ajax
// 获取用户表格数据
var getUserTableList = function (that, data) {
    var obj = {
        pageSize : 10,
        currentPage : 1,
    };
    data ? Object.assign(obj, data) : obj;
    dnsAjax.get({
        url : userManageDataUrl.user,
        data : data,
        success : function (response) {
            if (!response.data.users) return;
            that.tableUserData = addAttr(response.data.users);
            that.$refs.userPagination.setPage(pageNub(response.data.total), response.data.current_page);
        }
    });
};
// 获取角色表格数据
var getRoleTableList = function (that, data) {
    var obj = {
        pageSize : 10,
        currentPage : 1,
    };
    data ? Object.assign(obj, data) : obj;
    dnsAjax.get({
        url : userManageDataUrl.role,
        data : data,
        success : function (response) {
            sRelation(that, {
                isRelationLogic : [response],
            });
        }
    });
};
// 保存编辑
var editSave = function (that, data) {
    that.editUserVal.role_ids = JSON.parse('[' + that.editUserVal.role + ']');
    if (!validEditUser(that)) return;
    _.trim(that.editUserVal);
    dnsAjax.put({
        url : userManageDataUrl.user + '/' + that.nowEditId,
        data : that.editUserVal,
        success : function () {
            Toast.success('修改成功');
            getUserTableList(that);
            that.$refs.editDialogUser.hide();
        }
    });
};
// 为关联角色对象添加id和name的字段用于展示
var addAttr = function (users) {
    users.forEach(function (item) {
        if (!Array.isArray(item.roles)) return;
        // 添加展示的关联角色名字和角色id
        var addRoleId = [];
        var addRoleName = [];
        item.roles.forEach(function (a) {
            addRoleId.push(a.id);
            addRoleName.push(a.name);
        });
        item.role = addRoleId.join(',');
        item.roleName = strBr(this, addRoleName.join(','));
    });
    return users;
};
// 关联状态变化操作
var relationOperation = function (that, id, item) {
    var arr = JSON.parse('[' + that.editUserVal.role + ']');
    var arrName = [];
    that.editUserVal.roleName && arrName.push(that.editUserVal.roleName.split(','));
    arrName = _.flatten(arrName);
    // 创建独立的状态
    var nowState = arr.indexOf(id) != -1 ? sRelationState(true) : sRelationState(false);
    if (arr.indexOf(id) != -1) {
        var idx = arr.indexOf(id);
        arr.splice(idx, 1);
        arrName.splice(idx, 1);
    } else {
        arr.push(id);
        arrName.push(item.name);
    }
    nowState.currState(item);
    that.editUserVal.role = arr.join(',');
    that.editUserVal.roleName = strBr(that, arrName.join(','));
};
// 编辑表单验证
var validEditUser = function (that) {
    let errLen = that.$vform['editUser'].checkAll().length;
    that.$vform['editUser'].checkAll();
    return !errLen;
};
// 换行
var strBr = function (that, data) {
    var newArr = data.split(',');
    newArr.forEach((item, index, arr) => {
        if (!index) return;
        if (/\n/.test(item)) return;
        arr[index] = '\n' + item;
    });
    return newArr.join(',');
};
// 提交
var req = function (data) {
    // 提交数据处理
    var r = {};
    for (let key in data) r[key] = data[key].value;
    r = _.compact(r);
    r = _.trim(r);
    return r;
};
</script>

