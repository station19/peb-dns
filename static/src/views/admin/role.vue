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
            <btn @click="searchData('searchRoleData')">搜索</btn>
            <btn @click="resetRoleForm">重置</btn>
            <btn @click="addRole">添加</btn>
        </div>
        <vp-grid :head="tableRole.col" :data="tableRoleData" :colspan="4">
            <div :slot="'cell:option_'+i" v-for="(item,i) in tableRoleData">
                <btn size="small" @click="roleEdit(item.id, i)">编辑</btn>
                <btn size="small" type="danger" @click="delRole(item.id)">删除</btn>
            </div>
        </vp-grid>
        <vp-mnpager :show-short-cut="true" ref="rolePagination" v-on:to="rolePageTo" style="float: left"></vp-mnpager>
        <!-- 添加角色 -->
        <vp-dialog ref="addDialogRole" title="添加角色" @dialog:save="createRole">
            <div class="modal-body clearfix">
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>角色名称</label>
                    <input type="text" class="form-control" v-model="newRole.name" group="addRole" v-valid="{required:true}">
                </div>
                <div class="form-group" style="width: 50%;float:left">
                    <label>关联权限</label>
                    <textarea cols="30" rows="10" class="form-control" v-model="newRole.privilege_idsName" group="addRole" v-valid="{required:true}" disabled></textarea>
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
                    <btn @click="searchData('searchPrivilegeData')">搜索</btn>
                    <btn @click="resetPrivilegeForm">重置</btn>
                </div>
                <vp-grid :head="alertTablePrivilege.col" :data="tablePrivilegeData" :colspan="3">
                    <div :slot="'cell:option_'+i" v-for="(item,i) in tablePrivilegeData">
                        <btn :type="item.isDanger" size="small" @click="relation(2, item.id, item)">
                            <template v-if="item.isDanger">取消关联</template>
                            <template v-else>关联角色</template>
                        </btn>
                    </div>
                </vp-grid>
                <vp-mnpager :show-short-cut="true" ref="privilegePagination2" v-on:to="privilegePageTo" style="float: left"></vp-mnpager>
            </div>
        </vp-dialog>

        <!-- 编辑角色 -->
        <vp-dialog ref="editDialogRole" title="编辑角色" @dialog:save="modifyRole">
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
                    <btn @click="searchData('searchPrivilegeData')">搜索</btn>
                    <btn @click="resetPrivilegeForm">重置</btn>
                </div>
                <vp-grid :head="alertTablePrivilege.col" :data="tablePrivilegeData" :colspan="3">
                    <div :slot="'cell:option_'+i" v-for="(item,i) in tablePrivilegeData">
                        <btn :type="item.isDanger" size="small" @click="relation(1, item.id, item)">
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
    import {Datagrid, Pager, Select, Button, Toast, Valid, Alert, MiniPager} from 'vpui';
    import { searchData,relation,pageNub } from './methods.js';
    import Ajax from 'ajax';
    import './admin.css';
    import _ from '../../components/fn/tool';
    var adminAjax = new Ajax();
    var searchRoleDataEmpty = {
        id : {
            name : 'id',
            value : '',
        },
        name : {
            name : '角色名称',
            value : '',
        },
    }
    var searchPrivilegeDataEmpty = {
        id : {
            name : 'id',
            value : '',
            type : 'text'
        },
        name : {
            name : '权限名称',
            value : '',
            type : 'text'
        },
        operation : {
            name : '操作类型',
            display : ['访问', '修改', '删除'],
            value : '',
            type : 'select'
        },
        resource_type : {
            name : '资源类型',
            display : ['SERVER', 'VIEW', 'ZONE', 'RECORD', 'USER', 'ROLE', 'PRIVILEGE', 'PAGE'],
            value : '',
            type : 'select'
        },
        resource_id : {
            name : '资源ID',
            value : '',
            type : 'text'
        }
    }
    export default {
        data () {
            return {
                // 角色
                tableRole: {
                    col: {
                        id : {
                            label : 'id',
                            width : '100px'
                        },
                        name : '角色名称',
                        privilegeName : '关联权限',
                        option: {
                            type: 'action',
                            label: '操作',
                            width: '150px;'
                        }
                    },
                },
                // 搜索角色列表-展示搜索框
                searchRoleData : JSON.parse(JSON.stringify(searchRoleDataEmpty)),
                tableRoleData : [],
                // 弹窗角色
                alertTableRole: {
                    col: {
                        id : {
                            label : 'id',
                            width: '30px'
                        },
                        name : {
                            label: '角色名称',
                            width: '30px'
                        },
                        option: {
                            type: 'action',
                            label: '操作',
                            width: '10px'
                        }
                    },
                },
                // 添加角色
                newRole : {
                    name : '',
                    'privilege_ids' : '',
                    'privilege_idsName' : '',
                },
                // 编辑的角色
                editRoleVal : {
                    "name": "",
                    "privileges": ""
                },
                // 弹窗权限
                tablePrivilegeData : [],
                alertTablePrivilege: {
                    col: {
                        id : {
                            label : 'id',
                            width: '100px'
                        },
                        name : {
                            label: '权限名称',
                            width: '300px'
                        },
                        option: {
                            type: 'action',
                            label: '操作',
                            width: '45px'
                        }
                    },
                },
                searchPrivilegeData : JSON.parse(JSON.stringify(searchPrivilegeDataEmpty)),
                // 记录当前选择状态
                selectActive : {
                    user : 1,
                    role : 1,
                    privilege : 1,
                },
                // 编辑的用户
                editUserVal :{
                    "position":"",
                    "chinese_name": "",
                    "roles": [],
                    "cellphone":"",
                    "location":"",
                },
                // 添加还是编辑
                addEdit : '',
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
            this.searchData('searchRoleData', 1);
        },
        directives: {
            "valid":Valid,
        },
        methods: {
            resetRoleForm(){
                this.searchRoleData = JSON.parse(JSON.stringify(searchRoleDataEmpty));
            },
            resetPrivilegeForm(){
                this.searchPrivilegeData = JSON.parse(JSON.stringify(searchPrivilegeDataEmpty));
            },
            // 获取权限列表
            privilegeAjax (that, data, url, fn) {
                let self = this;
                adminAjax.get({
                    url : url,
                    data : data,
                    success : function (response) {
                        if (!response.data.privileges) return;
                        that.tablePrivilegeData = response.data.privileges;
                        // 处理操作类型映射
                        _.para(that.tablePrivilegeData, {
                            operation : ['访问', '修改', '删除'],
                            'resource_type' : ['SERVER', 'VIEW', 'ZONE', 'RECORD', 'USER', 'ROLE', 'PRIVILEGE', 'PAGE']
                        });
                        // 初始页数
                        var total = pageNub(response.data.total);
                        self.addEdit ? self.$refs.privilegePagination.setPage(total, response.data.current_page) : self.$refs.privilegePagination2.setPage(total, response.data.current_page)
                        fn && fn();
                    }
                });
            },
            // 添加表单验证
            validAddRole () {
                let errLen = this.$vform['addRole'].checkAll().length;
                this.$vform['addRole'].checkAll();
                return !errLen;
            },
            // 删除角色
            validEditRole () {
                let errLen = this.$vform['editRole'].checkAll().length;
                this.$vform['editRole'].checkAll();
                // !errLen && Toast.success('验证通过，发送请求', true);
                return !errLen;
            },
        
            delRole (index) {
                var that = this;
                Alert.confirm('确定要删除id是' + index + '的角色吗？', function () {
                    adminAjax.delete({
                        url : 'http://hfdns-test.ipo.com/admin/roles/' + index,
                        success : function () {
                            that.tableRoleData.splice(that.tableRoleData.indexOf(_.getObj(that.tableRoleData, 'id', index, true)), 1);
                            Toast.success('删除成功!');
                        }
                    });
                });
            },
            // 添加角色
            addRole () {
                this.addEdit = 0;
                this.searchData('searchPrivilegeData');
                this.$refs.addDialogRole.show();
                this.newRole = {
                    name : '',
                    'privilege_ids' : '',
                    'privilege_idsName' : '',
                }
            },
            createRole () {
                if (!this.validAddRole()) return;
                var that = this;
                var data = {
                    "name" : that.newRole.name,    //#角色名称
                    "privilege_ids" : that.newRole.privilege_ids.split(',')    //#权限ID列表
                }
                _.trim(data);
                adminAjax.post({
                    url : 'http://hfdns-test.ipo.com/admin/roles',
                    data : data,
                    success : function () {
                        Toast.success('添加成功');
                        that.getRoleList();
                    }
                });
                this.$refs.addDialogRole.hide();
            },
            // 编辑角色
            roleEdit (id, index) {
                this.addEdit = 1;
                this.$vform['editRole'].resetStyle();
                this.$refs.editDialogRole.show();
                this.searchData('searchPrivilegeData');
                this.modifyRole.id = id;
                this.modifyRole.index = index;
                this.editRoleVal = _.clone(this.tableRoleData[index]);
                // 关联名称换行显示
                var roleEditArr = this.editRoleVal.privilegeName.split(',');
                roleEditArr.forEach((item, index, arr) => {
                    if (!index) return;
                    if (/\n/.test(item)) return;
                    arr[index] = '\n' + item;
                });
                this.editRoleVal.privilegeName = roleEditArr.join(',');


                // 显示关联状态
                if (!this.editRoleVal.privilege) return;
                var arr = JSON.parse('[' + this.editRoleVal.privilege + ']');
                for (let key in this.tablePrivilegeData) {
                    if (arr.indexOf(this.tablePrivilegeData[key].id) != -1) {
                        this.tablePrivilegeData[key].isDanger = 'danger';
                    } else {
                        this.tablePrivilegeData[key].isDanger = '';
                    }
                }
            },
            modifyRole () {
                this.editRoleVal.privilege_ids = JSON.parse('[' + this.editRoleVal.privilege + ']');
                if (!this.validEditRole()) return;
                var that = this;
                _.trim(this.editRoleVal);
                adminAjax.put({
                    url : 'http://hfdns-test.ipo.com/admin/roles/' + this.modifyRole.id,
                    data : this.editRoleVal,
                    success : function () {
                        Toast.success('修改成功!');
                        for (let key in that.editRoleVal) that.tableRoleData[that.modifyRole.index][key] = that.editRoleVal[key];
                    }
                });
                this.$refs.editDialogRole.hide();
            },
            // 获取全部角色列表
            
            rolePageTo (index){
                // 获取角色分页列表
                this.searchData('searchRoleData', index);
            },
            privilegePageTo (index) {
                this.searchData('searchPrivilegeData', index);
            },
            // 获取全部权限列表
            getPrivilegeList () {
                this.privilegeAjax(this,{
                    pageSize : 10,
                    currentPage : 1
                }, 'http://hfdns-test.ipo.com/admin/privileges');
            },
            // 获取角色列表
            roleAjax (that, data, url, fn) {
                let self = this;
                adminAjax.get({
                    url : url,
                    data : data,
                    success : function (response) {
                        if (!response.data.roles) return;
                        response.data.roles.forEach(function (item) {
                            if (!Array.isArray(item.privileges)) return;
                            var itarr = [];
                            var itarr2 = [];
                            item.privileges.forEach(function (a) {
                                itarr.push(a.id);
                                itarr2.push(a.name);
                            });
                            // 要先绑才会监听，后绑不行
                            item.privilege = itarr.join(', ');
                            item.privilegeName = itarr2.join(', ');
                            item.isDanger = '';

                            // 关联名称换行显示
                            var roleEditArr = item.privilegeName.split(',');
                            roleEditArr.forEach((item, index, arr) => {
                                if (!index) return;
                                if (/\n/.test(item)) return;
                                arr[index] = '\n' + item;
                            });
                            item.privilegeName = roleEditArr.join(',');

                        });
                        that.tableRoleData = response.data.roles;
                        var val = 2222;
                        that.tableRoleData.forEach(function (item) {
                            item.select = {
                                value: val++,
                                checked: true
                            };
                        });
                        var total = pageNub(response.data.total);
                        self.$refs.rolePagination.setPage(total, response.data.current_page);
                        // 初始页数
                        fn && fn();
                    }
                });
            },
            searchData,
            relation
        }
    }





</script>