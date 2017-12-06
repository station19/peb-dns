<template>
    <div id='admin' class="admin-block">
        <h1 style="background-color:GoldEnrod;">权限</h1>
        <div class="grid-search-form">
            <input 
                class="search-item"
                type="text" 
                :placeholder="value.name" 
                v-model="searchPrivilegeData[key].value" 
                v-for="(value, key, index) in searchPrivilegeData" 
                :test="value['type']" v-if="value['type']=='text'">
            </input>
            <select class="search-item" v-model="searchPrivilegeData[key].value" v-else>
                <option v-for="(item, i) in value.display" :value="i">{{item}}</option>
            </select>
            <btn @click="searchData">搜索</btn>
            <btn @click="resetForm">重置</btn>
            <btn @click="addPrivilege">添加</btn>
        </div>
        <vp-grid :head="tablePrivilege.col" :data="tablePrivilegeData" :colspan="7">
            <div :slot="'cell:option_'+i" v-for="(item,i) in tablePrivilegeData">
                <btn size="small" @click="privilegeEdit(item.id, i)">编辑</btn>
                <btn size="small" type="danger" @click="delPrivilege(item.id)">删除</btn>
            </div>
        </vp-grid>
        <vp-mnpager :show-short-cut="true" ref="privPagination" v-on:to="privPageTo" style="float: left"></vp-mnpager>
        <vp-dialog ref="editDialogPrivilege" title="titleName" @dialog:save="savePrivilege">
            <div class="modal-body clearfix">
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>权限名称</label>
                    <input type="text" class="form-control" v-model="editPrivilegeVal.name" v-valid="{required:true}" group="editPrivilege">
                </div>
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>操作类型</label>
                    <select id="s_type" class="form-control" v-model="editPrivilegeVal.operation" v-valid="{required:true}" group="editPrivilege">
                        <option value="0">访问</option>
                        <option value="1">修改</option>
                        <option value="2">删除</option>
                    </select>
                </div>
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>资源类型</label>
                    <select id="s_type" class="form-control" v-model="editPrivilegeVal.resource_type" v-valid="{required:true}" group="editPrivilege">
                        <option value="0">SERVER</option>
                        <option value="1">VIEW</option>
                        <option value="2">ZONE</option>
                        <option value="3">RECORD</option>
                        <option value="4">USER</option>
                        <option value="5">ROLE</option>
                        <option value="6">PRIVILEGE</option>
                        <option value="7">PAGE</option>
                    </select>
                </div>
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>资源ID</label>
                    <input type="text" class="form-control" v-model="editPrivilegeVal.resource_id">
                </div>
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>备注</label>
                    <input type="text" class="form-control" v-model="editPrivilegeVal.comment">
                </div>
            </div>
        </vp-dialog>
    </div>
</template>
<script>
import dialog from '../_complex/dialog.vue';
import {Datagrid, Pager, Select, Button, Toast, Valid, Radio, Checkbox, Alert, MiniPager} from 'vpui';
import { pageNub } from './methods.js';
import Ajax from 'ajax';
import './admin.css';
import _ from '../../components/fn/tool';
import dnsData from '../dnsData';

var dnsAjax = new Ajax();
var privilegeManage = dnsData('privilegeManage');
var privilegeManageUrl = dnsData('url');

export default {
    data () {
        return {
            addOrEdit : '',
            // 标题
            titleName : '',
            // 权限表体
            tablePrivilegeData : [],
            // 权限表头
            tablePrivilege: privilegeManage.tablePrivilege,
            // 单个权限
            editPrivilegeVal : sReset(privilegeManage.editPrivilegeVal),
            // 权限搜索框
            searchPrivilegeData : sReset(privilegeManage.searchPrivilegeDataEmpty)
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
        // 添加权限
        addPrivilege () {
            sAdd(this);
        },
        // 编辑权限
        privilegeEdit (id, index) {
            sEdit(this, {
                isEditLogic : [index]
            });
        },
        // 保存编辑
        savePrivilege () {
            if (!validPrivilege(this)) return;
            isAddOrEdit(this.addOrEdit) ? editSave(this) : addSave(this);
        },
        // 删除权限
        delPrivilege (id) {
            delNoice(this, id);
        },
        // 分页
        privPageTo (index){
            getTableList(this, {
                currentPage : index
            });
        },
        // 搜索
        searchData () {
            getTableList(this, req(this.searchPrivilegeData));
        },
        // 重置
        resetForm () {
            this.searchPrivilegeData = sReset(privilegeManage.searchPrivilegeDataEmpty)
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
var sEdit = _.decorate(function isEditActive (id) {
    this.addOrEdit = 1;
});

// 初始状态
var sInit = function (that) {
    getTableList(that);
    // 添加privilege
    sAdd.add(function isAddLogic () {
        this.editPrivilegeVal = sReset(privilegeManage.editPrivilegeVal),
        this.$refs.editDialogPrivilege.show();
        this.titleName = '添加权限';
        this.$vform['editPrivilege'].resetStyle();
    });
    // 编辑privilege
    sEdit.add(function isEditLogic (index) {
        this.editPrivilegeVal = _.para(Object.assign({}, this.tablePrivilegeData[index]), {
            operation : _.invert(this.searchPrivilegeData.operation.display),
            resource_type : _.invert(this.searchPrivilegeData.resource_type.display),
        });
        this.titleName = '编辑权限';
        this.$vform['editPrivilege'].resetStyle();
        this.$refs.editDialogPrivilege.show();
    });
};

// 重置状态
var sReset = function (data) {
    return JSON.parse(JSON.stringify(data));
};

// 分支
var isAddOrEdit = _.val;

// ajax
// 获取表格数据
var getTableList = function (that, data) {
    var obj = {
        pageSize : 10,
        currentPage : 1,
    };
    data ? Object.assign(obj, data) : obj;
    dnsAjax.get({
        url: privilegeManageUrl.privilege,
        data : data,
        success : function (response) {
            if (!response.data.privileges) return;
            that.tablePrivilegeData = response.data.privileges;
            _.para(that.tablePrivilegeData, {
                operation : that.searchPrivilegeData.operation.display,
                'resource_type' : that.searchPrivilegeData.resource_type.display
            });
            that.$refs.privPagination.setPage(pageNub(response.data.total), response.data.current_page);
        }
    });
};
// 添加保存
var addSave = function (that, data) {
    _.trim(that.editPrivilegeVal);
    dnsAjax.post({
        url : privilegeManageUrl.role,
        data : that.editPrivilegeVal,
        success : function (response) {
            Alert('添加成功');
            getTableList(that);
        }
    });
    that.$refs.editDialogPrivilege.hide();
};
// 编辑保存
var editSave = function (that, data) {
    _.trim(that.editPrivilegeVal);
    dnsAjax.put({
        url : privilegeManageUrl.privilege + '/' + that.editPrivilegeVal.id,
        data : that.editPrivilegeVal,
        success : function () {
            Toast.success('修改成功');
            getTableList(that);
        }
    });
    that.$refs.editDialogPrivilege.hide();
};
// 通知
var delNoice = function (that, id) {
    Alert.confirm('确定要删除id是' + id + '的权限吗？', function () {
        dnsAjax.delete({
            url : privilegeManageUrl.privilege + '/' + id,
            success : function () {
                getTableList(that);
                Toast.success('删除成功');
            }
        });
    });
};
// 提交
var req = function (data) {
    // 提交数据处理
    var r = {};
    for (let key in data) r[key] = data[key].value + '';
    r = _.compact(r);
    r = _.trim(r);
    return r;
};
// 验证
var validPrivilege = function (that) {
    let errLen = that.$vform['editPrivilege'].checkAll().length;
    that.$vform['editPrivilege'].checkAll();
    return !errLen;
};
</script>