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
            <btn  @click="searchData('searchUserData')">搜索</btn>
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
                        <btn @click="searchData('searchRoleData')" style="margin-right:5px;">搜索</btn><btn @click="resetRoleForm">重置</btn>
                    </div>
                    <vp-grid :head="alertTableRole.col" :data="tableRoleData" :colspan="3" style="margin-bottom: 22px;">
                        <div :slot="'cell:option_'+i" v-for="(item,i) in tableRoleData">
                            <btn :type="item.isDanger" size="small" @click="relation(0, item.id, item)">
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
    import { searchData,relation,pageNub } from './methods.js';
    import {Datagrid, Pager, Select, Button, Toast, Valid, Radio, Checkbox, Alert, MiniPager} from 'vpui';
    import Ajax from 'ajax';
    import _ from '../../components/fn/tool';
    var adminAjax = new Ajax();
    var searchUserDataEmpty = {
        id : { name : 'id',value : '' },
        username : { name : '用户名',value : ''},
        chinese_name : { name : '中文名称',value : ''},
        cellphone : { name : '手机号码',value : '' }
    };
    var searchRoleDataEmpty = {
        id : {
            name : 'id',
            value : '',
        },
        name : {
            name : '角色名称',
            value : '',
        }
    };
    export default {
        data () {
            return {
                // 用户
                tableUser: {
                    col: {
                        id : {
                            label : 'id',
                            width : '100px'
                        },
                        username : '用户名',
                        roleName : '关联角色',
                        'chinese_name' : '中文名称',
                        cellphone : '手机号码',
                        position : '职位',
                        location : '地址',
                        email : '邮箱',
                        member_since : '首次登录时间',
                        last_seen : '最近登录时间',
                        // rolesId : '关联角色id',
                        // rolesName : '关联角色名称',
                        option: {
                            type: 'action',
                            label: '操作',
                            width: '120px;'
                        }
                    },
                    colspan: 11
                },
                tableUserData: [],
                // 搜索用户列表-展示搜索框
                searchUserData: JSON.parse(JSON.stringify(searchUserDataEmpty)),
                // 编辑的用户
                editUserVal: {
                    "position": "",
                    "chinese_name": "",
                    "roles": [],
                    "cellphone": "",
                    "location": "",
                },
                // 搜索角色列表-展示搜索框
                searchRoleData: JSON.parse(JSON.stringify(searchRoleDataEmpty)),
                tableRoleData: [],
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
                            width: '20px'
                        }
                    },
                }
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
            this.fetchUserInit();
        },
        directives: {
            "valid":Valid,
        },
        methods: {
            resetForm(){
                this.searchUserData = JSON.parse(JSON.stringify(searchUserDataEmpty));
            },
            resetRoleForm(){
                this.searchRoleData = JSON.parse(JSON.stringify(searchRoleDataEmpty));
            },
            fetchUserInit () {
                this.fetchUser(this, {
                    pageSize : 10,
                    currentPage : 1
                }, 'http://hfdns-test.ipo.com/admin/users');
            },
            
            // 获取用户列表
            fetchUser (that, data, url) {
                let self = this;
                adminAjax.get({
                    url : url,
                    data : data,
                    success : function (response) {
                        if (!response.data.users) return;
                        that.tableUserData = response.data.users;
                        that.tableUserData.forEach(function (item) {
                            if (!Array.isArray(item.roles)) return;
                            var itarr = [];
                            var itarr2 = [];
                            item.roles.forEach(function (a) {
                                itarr.push(a.id);
                                itarr2.push(a.name);
                            });
                            itarr.push();
                            item.role = itarr.join(',');
                            item.roleName = itarr2.join(',');
                        });
                        
                        // 初始页数
                        var total = pageNub(response.data.total);
                        self.$refs.userPagination.setPage(total, response.data.current_page);
                    }
                });
            },
            // 编辑用户
            userEdit (id, index) {
                this.$refs.editDialogUser.show();
                this.$vform['editUser'].resetStyle();
                this.modifyUser.id = id;
                this.modifyUser.index = index;
                // this.editUserVal = this.tableUserData[index];
                this.editUserVal = _.clone(this.tableUserData[index]);

                // 过滤null，验证组件默认是有的
                for (var key in this.editUserVal) {
                    if (this.editUserVal[key] === null) this.editUserVal[key] = '';
                }

                // 关联名称换行显示
                var userEditArr = this.editUserVal.roleName.split(',');
                userEditArr.forEach((item, index, arr) => {
                    if (!index) return;
                    if (/\n/.test(item)) return;
                    arr[index] = '\n' + item;
                });
                this.editUserVal.roleName = userEditArr.join(',');


                this.getRoleList();
                // 显示关联角色按钮状态
                var arr = JSON.parse('[' + this.editUserVal.role + ']');
                for (let key in this.tableRoleData) {
                    if (arr.indexOf(this.tableRoleData[key].id) != -1) {
                        this.tableRoleData[key].isDanger = 'danger';    
                    } else {
                        this.tableRoleData[key].isDanger = '';
                    }
                }
            },
            // 编辑表单验证
            validEditUser () {
                let errLen = this.$vform['editUser'].checkAll().length;
                this.$vform['editUser'].checkAll();
                // !errLen && Toast.success('验证通过，发送请求', true);
                return !errLen;
            },
            modifyUser () {
                this.editUserVal.role_ids = JSON.parse('[' + this.editUserVal.role + ']');
                if (!this.validEditUser()) return;
                var that = this;
                _.trim(this.editUserVal);
                adminAjax.put({
                    url : 'http://hfdns-test.ipo.com/admin/users/' + this.modifyUser.id,
                    data : this.editUserVal,
                    success : function () {
                        Toast.success('修改成功');
                        for (let key in that.editUserVal) that.tableUserData[that.modifyUser.index][key] = that.editUserVal[key];
                    }
                });
                this.$refs.editDialogUser.hide();
            },
            // 获取全部角色列表
            getRoleList () {
                var tableRole = document.querySelector('.role table');
                var self = this;
                if (tableRole) tableRole.rows[this.selectActive.role].style.backgroundColor = 'transparent';
                this.roleAjax(this, {
                    pageSize : 10,
                    currentPage : 1
                }, 'http://hfdns-test.ipo.com/admin/roles', function () {
                    if (!this.editUserVal.role) return;
                    var arr = JSON.parse('[' + this.editUserVal.role + ']');
                    for (let key in this.tableRoleData) {
                        if (arr.indexOf(this.tableRoleData[key].id) != -1) {
                            this.tableRoleData[key].isDanger = 'danger';    
                        } else {
                            this.tableRoleData[key].isDanger = '';
                        }
                    }
                }.bind(this));
            },
            rolePageTo (index){
                this.searchData('searchRoleData', index);
            },
            userPageTo (index){
                this.fetchUser(this, {
                    currentPage : index
                }, 'http://hfdns-test.ipo.com/admin/users');
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
                        response.data.roles.forEach(function (item, index, arr) {
                            if (!Array.isArray(item.privileges)) return;
                            var itarr = [];
                            item.privileges.forEach(function (a, b, c) {
                                itarr.push(a.id);
                            });
                            // 要先绑才会监听，后绑不行
                            item.privilege = itarr.join(', ');
                            item.isDanger = '';
                        });
                        that.tableRoleData = response.data.roles;
                        var val = 2222;
                        that.tableRoleData.forEach(function (item, index, arr) {
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
            pageToRole (i) {
                // 获取角色分页列表
                this.roleAjax(this, {
                    currentPage : i
                }, 'http://hfdns-test.ipo.com/admin/roles', function () {
                    // 显示关联角色按钮状态
                    // 我怎么知道是弹窗
                    // 管他是不是弹窗，反正外面没有写那个按钮的渲染
                    if (!this.editUserVal.role) return;
                    var arr = JSON.parse('[' + this.editUserVal.role + ']');
                    for (let key in this.tableRoleData) {
                        if (arr.indexOf(this.tableRoleData[key].id) != -1) {
                            this.tableRoleData[key].isDanger = 'danger';    
                        } else {
                            this.tableRoleData[key].isDanger = '';
                        }
                    }
                }.bind(this));
            },
            searchData,
            relation
        }
    }
</script>

