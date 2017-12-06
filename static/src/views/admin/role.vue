<template>
    <div id='admin' class="admin-block">
        <h1 style="background-color:LightGreen;">角色</h1>
        <div class="grid-search-form">
            <input 
                class="search-item"
                type="text" 
                :placeholder="value.name" 
                v-model="searchRoleData[key].value" 
                v-for="(value, key, index) in searchRoleData">
            </input>
            <btn @click="searchRole">搜索</btn>
            <btn @click="resetRoleForm">重置</btn>
            <btn @click="addRole">添加</btn>
        </div>
        <vp-grid :head="tableRole.col" :data="tableRoleData" :colspan="4">
            <div :slot="'cell:option_'+i" v-for="(item,i) in tableRoleData">
                <btn size="small" @click="roleEdit(i)">编辑</btn>
                <btn size="small" type="danger" @click="delRole(item.id)">删除</btn>
            </div>
        </vp-grid>
        <vp-mnpager :show-short-cut="true" ref="rolePagination" v-on:to="rolePageTo" style="float: left"></vp-mnpager>
        <!-- 添加角色 -->
        <vp-dialog ref="addDialogRole" title="添加角色" @dialog:save="saveRole">
            <div class="modal-body clearfix">
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>角色名称</label>
                    <input type="text" class="form-control" v-model="editRoleVal.name" group="addRole" v-valid="{required:true}">
                </div>
                <div class="form-group" style="width: 50%;float:left">
                    <label>关联权限</label>
                    <textarea cols="30" rows="10" class="form-control" v-model="editRoleVal.privilegeName" group="addRole" v-valid="{required:true}" disabled></textarea>
                </div>
                <div class="grid-search-form">
                    <input 
                        class="search-item"
                        type="text" 
                        :placeholder="value.name" 
                        v-model="searchPrivilegeData[key].value" 
                        v-for="(value, key, index) in searchPrivilegeData" 
                        :test="value['type']" v-if="value['type']=='text'"
                        :style="'width:'+ ((value.name == '权限名称') ? '62px; width:300px;' : '100px;')"
                    >
                    </input>
                    <btn @click="searchPrivilege">搜索</btn>
                    <btn @click="resetPrivilegeForm">重置</btn>
                </div>
                <vp-grid :head="tablePrivilege.col" :data="tablePrivilegeData" :colspan="3">
                    <div :slot="'cell:option_'+i" v-for="(item,i) in tablePrivilegeData">
                        <btn :type="item.isDanger" size="small" @click="relation(item.id, item)">
                            <template v-if="item.isDanger">取消关联</template>
                            <template v-else>关联角色</template>
                        </btn>
                    </div>
                </vp-grid>
                <vp-mnpager :show-short-cut="true" ref="privilegePagination2" v-on:to="privilegePageTo" style="float: left"></vp-mnpager>
            </div>
        </vp-dialog>

        <!-- 编辑角色 -->
        <vp-dialog ref="editDialogRole" title="编辑角色" @dialog:save="saveRole">
            <div class="clearfix">
                <div class="clearfix">
                    <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                        <label>角色名称</label>
                        <input type="text" class="form-control" v-model="editRoleVal.name" group="editRole" v-valid="{required:true}">
                    </div>
                    <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                        <label>关联权限名称</label>
                        <textarea cols="30" rows="10" disabled class="form-control" v-model="editRoleVal.privilegeName" group="editRole" v-valid="{required:true}"></textarea>
                    </div>
                </div>
                <div class="grid-search-form">
                    <input 
                        class="search-item"
                        type="text" 
                        :placeholder="value.name" 
                        v-model="searchPrivilegeData[key].value" 
                        v-for="(value, key, index) in searchPrivilegeData" 
                        :test="value['type']" v-if="value['type']=='text'"
                        :style="'width:'+ ((value.name == '权限名称') ? '62px; width:300px;' : '100px;')"
                    >
                    </input>
                    <btn @click="searchPrivilege">搜索</btn>
                    <btn @click="resetPrivilegeForm">重置</btn>
                </div>
                <vp-grid :head="tablePrivilege.col" :data="tablePrivilegeData" :colspan="3">
                    <div :slot="'cell:option_'+i" v-for="(item,i) in tablePrivilegeData">
                        <btn :type="item.isDanger" size="small" @click="relation(item.id, item)">
                            <template v-if="item.isDanger">取消关联</template>
                            <template v-else>关联角色</template>
                        </btn>
                    </div>
                </vp-grid>
                <vp-mnpager :show-short-cut="true" ref="privilegePagination" v-on:to="privilegePageTo" style="float: left"></vp-mnpager>
            </div>
        </vp-dialog>
    </div>
</template>
<script>
import dialog from '../_complex/dialog.vue';
import './admin.css';
import {Datagrid, Pager, Select, Button, Toast, Valid, Alert, MiniPager} from 'vpui';
import { searchData,relation,pageNub } from './methods';
import Ajax from 'ajax';
import _ from '../../components/fn/tool';
import dnsData from '../dnsData';

var dnsAjax = new Ajax();
var roleManage = dnsData('roleManage');
var roleManageUrl = dnsData('url');

    export default {
        data () {
            return {
                addOrEdit : '',
                // 角色表头
                tableRole: roleManage.tableRole,
                // 搜索角色列表-展示搜索框
                searchRoleData : sReset(roleManage.searchRoleDataEmpty),
                // 角色表体
                tableRoleData : [],
                // 编辑的单个角色
                editRoleVal : sReset(roleManage.editRoleVal),
                // 权限表体
                tablePrivilegeData : [],
                // 权限表头
                tablePrivilege: roleManage.tablePrivilege,
                // 权限搜索框
                searchPrivilegeData : sReset(roleManage.searchPrivilegeDataEmpty),
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
            // 重置角色
            resetRoleForm(){
                this.searchRoleData = sReset(roleManage.searchRoleDataEmpty);
            },
            // 重置权限
            resetPrivilegeForm(){
                this.searchPrivilegeData = sReset(roleManage.searchPrivilegeDataEmpty);
            },
            // 删除角色
            delRole (id) {
                delNoice(this, id);
            },
            // 添加角色
            addRole () {
                sAdd(this);
            },
            // 编辑角色
            roleEdit (index) {
                sEdit(this, {
                    isEditLogic : [index]
                });
            },
            // 保存角色
            saveRole () {
                
            },
            // 保存编辑
            saveRole () {
                if (isAddOrEdit(this.addOrEdit)) {
                    if (!valid(this, 'editRole')) return;
                    editSave(this);
                } else {
                    if (!valid(this, 'addRole')) return;
                    addSave(this);
                }
                
            },
            // 角色分页
            rolePageTo (index){
                getRoleTableList(this, {
                    currentPage : index
                });
            },
            // 权限分页
            privilegePageTo (index) {
                getPrivilegeTableList(this, {
                    currentPage : index
                });
            },
            // 角色搜索
            searchRole () {
                getRoleTableList(this, req(this.searchRoleData));
            },
            // 权限搜索
            searchPrivilege () {
                getPrivilegeTableList(this, req(this.searchPrivilegeData))
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
// 当前状态
/*
this.addOrEdit----编辑操作还是添加操作
0----添加
1----编辑
*/
var sAdd = _.decorate(function isAddActive () {
    this.addOrEdit = 0;
});
var sEdit = _.decorate(function isEditActive () {
    this.addOrEdit = 1;
});
// 编辑用户的关联状态
var sRelation = _.decorate(function isRelationActive () {
    // 显示关联权限按钮状态
    if (!this.editRoleVal.privilege) return;
    var arr = JSON.parse('[' + this.editRoleVal.privilege + ']');
    for (let key in this.tablePrivilegeData) {
        arr.indexOf(this.tablePrivilegeData[key].id) != -1 ? this.tablePrivilegeData[key].isDanger = 'danger' : this.tablePrivilegeData[key].isDanger = '';
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
    getRoleTableList(that);
    // 添加role
    sAdd.add(function isAddLogic() {
        this.$vform['addRole'].resetStyle();
        this.$refs.addDialogRole.show();
        this.editRoleVal = sReset(roleManage.editRoleVal);
        getPrivilegeTableList(this);
    });
    // 编辑role
    sEdit.add(function isEditLogic (index) {
        this.$vform['editRole'].resetStyle();
        this.$refs.editDialogRole.show();
        this.editRoleVal = _.clone(this.tableRoleData[index]);
        getPrivilegeTableList(this);
    });
    // 编辑role的table
    sRelation.add(function isRelationLogic (response) {
        if (!response.data.privileges) return;
        that.tablePrivilegeData = response.data.privileges;
        _.para(that.tablePrivilegeData, {
            operation : that.searchPrivilegeData.operation.display,
            'resource_type' : that.searchPrivilegeData.resource_type.display
        });
        // 添加isDanger
        response.data.privileges.forEach(function (item, index, arr) {
            item.isDanger = '';
        });
        var total = pageNub(response.data.total);
        that.addOrEdit ? that.$refs.privilegePagination.setPage(total, response.data.current_page) : that.$refs.privilegePagination2.setPage(total, response.data.current_page)
    });
};

// 重置状态
var sReset = function (data) {
    return JSON.parse(JSON.stringify(data));
};

// 分支
var isAddOrEdit = _.val;

// ajax
// 获取角色表格数据
var getRoleTableList = function (that, data) {
    var obj = {
        pageSize : 10,
        currentPage : 1,
    };
    data ? Object.assign(obj, data) : obj;
    dnsAjax.get({
        url : roleManageUrl.role,
        data : data,
        success : function (response) {
            if (!response.data.roles) return;
            that.tableRoleData = addAttr(that, response.data.roles);
            that.$refs.rolePagination.setPage(pageNub(response.data.total), response.data.current_page);
        }
    });
};
// 获取权限表格数据
var getPrivilegeTableList = function (that, data) {
    var obj = {
        pageSize : 10,
        currentPage : 1,
    };
    data ? Object.assign(obj, data) : obj;
    dnsAjax.get({
        url : roleManageUrl.privilege,
        data : data,
        success : function (response) {
            sRelation(that, {
                isRelationLogic : [response],
            });
        }
    });
};
// 添加保存
var addSave = function (that, data) {
    that.editRoleVal.privilege_ids = that.editRoleVal.privilege.split(',');
    _.trim(data);
    dnsAjax.post({
        url : roleManageUrl.role,
        data : that.editRoleVal,
        success : function () {
            Toast.success('添加成功');
            getRoleTableList(that);
            that.$refs.addDialogRole.hide();
        }
    });
};
// 编辑保存
var editSave = function (that, data) {
    that.editRoleVal.privilege_ids = JSON.parse('[' + that.editRoleVal.privilege + ']');
    _.trim(that.editRoleVal);
    dnsAjax.put({
        url : roleManageUrl.role + '/' + that.editRoleVal.id,
        data : that.editRoleVal,
        success : function () {
            Toast.success('修改成功!');
            that.$refs.editDialogRole.hide();
            getRoleTableList(that);
        }
    });
};
// 关联状态变化操作
var relationOperation = function (that, id, item) {
    if (!that.editRoleVal.privilege) that.editRoleVal.privilege = '';
    var arr = JSON.parse('[' + that.editRoleVal.privilege + ']');
    var arrName = [];
    that.editRoleVal.privilegeName && arrName.push(that.editRoleVal.privilegeName.split(','));
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
    that.editRoleVal.privilege = arr.join(',');
    that.editRoleVal.privilegeName = strBr(that, arrName.join(','));
};
// 为关联权限对象添加id和name的字段用于展示
var addAttr = function (that, roles) {
    roles.forEach(function (item) {
        if (!Array.isArray(item.privileges)) return;
        // 添加展示的关联权限名字和权限id
        var addPrivilegeId = [];
        var addPrivilegeName = [];
        item.privileges.forEach(function (a) {
            addPrivilegeId.push(a.id);
            addPrivilegeName.push(a.name);
        });
        item.privilege = addPrivilegeId.join(', ');
        item.privilegeName = strBr(that, addPrivilegeName.join(','));
    });
    return roles;
};
// 通知
var delNoice = function (that, id) {
    Alert.confirm('确定要删除id是' + id + '的角色吗？', function () {
        dnsAjax.delete({
            url : roleManageUrl.role + '/' + id,
            success : function () {
                getRoleTableList(that);
                Toast.success('删除成功!');
            }
        });
    });
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
// 验证
var valid = function (that, str) {
    let errLen = that.$vform[str].checkAll().length;
    that.$vform[str].checkAll();
    return !errLen;
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