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
                <option v-for="(item, i) in value.display" :value="item == '全部' ? '' : i - 1">{{item}}</option>
            </select>
            <btn @click="searchData('searchPrivilegeData')">搜索</btn>
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
        <!-- 添加权限 -->
        <vp-dialog ref="addDialogPrivilege" title="添加权限" @dialog:save="createPrivilege">
            <div class="modal-body clearfix">
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>权限名称</label>
                    <input type="text" class="form-control" v-model="newPrivilege.name" v-valid="{required:true}" group="addPrivilege">
                </div>
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>操作类型</label>
                    <select id="s_type" class="form-control" v-model="newPrivilege.operation">
                        <option value="0">访问</option>
                        <option value="1">修改</option>
                        <option value="2">删除</option>
                    </select>
                </div>
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>资源类型</label>
                    <select id="s_type" class="form-control" v-model="newPrivilege.resource_type">
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
                    <input type="text" class="form-control" v-model="newPrivilege.resource_id">
                </div>
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>备注</label>
                    <input type="text" class="form-control" v-model="newPrivilege.comment">
                </div>
            </div>
        </vp-dialog>


        <!-- 编辑权限 -->
        <vp-dialog ref="editDialogPrivilege" title="编辑权限" @dialog:save="modifyPrivilege">
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
                    <input type="text" class="form-control" v-model="editPrivilegeVal.resource_id" v-valid="{required:true}" group="editPrivilege">
                </div>
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>备注</label>
                    <input type="text" class="form-control" v-model="editPrivilegeVal.comment" v-valid="{required:true}" group="editPrivilege">
                </div>
            </div>
        </vp-dialog>
    </div>
</template>
<script>
    import dialog from '../_complex/dialog.vue';
    import {Datagrid, Pager, Select, Button, Toast, Valid, Radio, Checkbox, Alert, MiniPager} from 'vpui';
    import { searchData,relation,pageNub } from './methods.js';
    import Ajax from 'ajax';
    import './admin.css';
    import _ from '../../components/fn/tool';
    var adminAjax = new Ajax();
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
            display : ['全部', '访问', '修改', '删除'],
            value : '',
            type : 'select'
        },
        resource_type : {
            name : '资源类型',
            display : ['全部', 'SERVER', 'VIEW', 'ZONE', 'RECORD', 'USER', 'ROLE', 'PRIVILEGE', 'PAGE'],
            value : '',
            type : 'select'
        },
        resource_id : {
            name : '资源ID',
            value : '',
            type : 'text'
        }
    }
    var  newPrivilegeEmpty = {
        "name": "",     //#权限名称
        "operation": '',    //#操作类型
        "resource_type": '',    //#资源类型
        "resource_id": '',     //#资源ID
        "comment": "",
    }
    export default {
        data () {
            return {
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
                // 权限
                tablePrivilege: {
                    col: {
                        id : {
                            label : 'id',
                            width : '100px'
                        },
                        name : {
                            label: '权限名称',
                            width: '280px'
                        },
                        operation : {
                            label: '操作类型',
                            width: '100px;'
                        },
                        'resource_type' : {
                            label: '资源类型',
                            width: '100px;'
                        },
                        'resource_id' : {
                            label: '资源ID',
                            width: '80px'
                        },
                        comment : '备注',
                        option: {
                            type: 'action',
                            label: '操作',
                            width: '150px'
                        }
                    },
                },
                privilegePager: {
                    current: 1,
                    total: 10,
                    volumn: 6
                },
                // 新的权限
                newPrivilege : JSON.parse(JSON.stringify(newPrivilegeEmpty)),
                // 编辑的角色
                editRoleVal : {
                    "name": "",
                    "privileges": ""
                },
                // 编辑的权限
                editPrivilegeVal : {
                    "name": "",   //#权限名称
                    "operation": '',   //#操作类型
                    "resource_type": '',   //#资源类型
                    "resource_id": '',  //#资源ID
                    "comment": "",   //#备注
                },
                // 记录当前选择状态
                selectActive : {
                    user : 1,
                    role : 1,
                    privilege : 1,
                },
                searchPrivilegeData : JSON.parse(JSON.stringify(searchPrivilegeDataEmpty))
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
            this.searchData('searchPrivilegeData', 1);
        },

        directives: {
            "valid":Valid,
        },
        methods: {
            resetForm () {
                this.searchPrivilegeData = JSON.parse(JSON.stringify(searchPrivilegeDataEmpty))
            },
            // 添加权限
            addPrivilege () {
                this.newPrivilege = JSON.parse(JSON.stringify(newPrivilegeEmpty)),
                this.$refs.addDialogPrivilege.show();
            },
            // 获取全部权限列表
            getPrivilegeList () {
                this.privilegeAjax(this,{
                    pageSize : 10,
                    currentPage : 1
                }, 'http://hfdns-test.ipo.com/admin/privileges');
            },
        
            validAddPrivilege () {
                let errLen = this.$vform['addPrivilege'].checkAll().length;
                this.$vform['addPrivilege'].checkAll();
                // !errLen && Toast.success('验证通过，发送请求', true);
                return !errLen;
            },
        
            validEditPrivilege () {
                let errLen = this.$vform['editPrivilege'].checkAll().length;
                this.$vform['editPrivilege'].checkAll();
                // !errLen && Toast.success('验证通过，发送请求', true);
                return !errLen;
            },

            pageToPrivilege (i) {
                // 获取权限分页列表
                this.privilegeAjax(this, {
                    currentPage : i
                }, 'http://hfdns-test.ipo.com/admin/privileges', function () {
                    if (!this.editRoleVal.privilege) return;
                    var arr = JSON.parse('[' + this.editRoleVal.privilege + ']');
                    for (let key in this.tablePrivilegeData) {
                        if (arr.indexOf(this.tablePrivilegeData[key].id) != -1) {
                            this.tablePrivilegeData[key].isDanger = 'danger';    
                        } else {
                            this.tablePrivilegeData[key].isDanger = '';
                        }
                    }
                }.bind(this));
            },

            createPrivilege () {
                if (!this.validAddPrivilege()) return;
                _.trim(this.newPrivilege);
                adminAjax.post({
                    url : 'http://hfdns-test.ipo.com/admin/roles',
                    data : this.newPrivilege,
                    success : function (response) {
                        Alert('添加成功');
                    }
                });
                this.$refs.addDialogPrivilege.hide();
            },
        
            // 编辑权限
            privilegeEdit (id, index) {
                // 填充当前数据
                // 为什么不直接引用是因为operation有映射关系，初始页面的时候我已经把值映射为中文了，现在要数字所以要映射回来，如果用引用，那么原来初始的中文会变数字就反掉了
                var that = this;
                this.editPrivilegeVal.name = this.tablePrivilegeData[index].name;
                var nb = _.para(Object.assign({}, this.tablePrivilegeData[index]), {
                    operation : _.invert(that.searchPrivilegeData.operation.display),
                    resource_type : _.invert(that.searchPrivilegeData.resource_type.display),
                });
                this.editPrivilegeVal.operation = nb.operation;
                this.editPrivilegeVal.resource_type = nb.resource_type;
                this.editPrivilegeVal.resource_id = this.tablePrivilegeData[index].resource_id;
                this.editPrivilegeVal.comment = this.tablePrivilegeData[index].comment ? this.tablePrivilegeData[index].comment : '';

                // 解决点了一个弹框有必填提示后关掉弹框，再开另一个弹框的时候把刚刚必填的提示带过去了
                this.validEditPrivilege();

                this.$vform['editPrivilege'].resetStyle();
                this.$refs.editDialogPrivilege.show();
                this.modifyPrivilege.id = id;
                this.modifyPrivilege.index = index;
            },
            modifyPrivilege () {
                if (!this.validEditPrivilege()) return;
                var that = this;
                var data = {
                    "name": this.editPrivilegeVal.name,   //#权限名称
                    "operation": this.editPrivilegeVal.operation,   //#操作类型
                    "resource_type": this.editPrivilegeVal.resource_type,   //#资源类型
                    "resource_id": this.editPrivilegeVal.resource_id,  //#资源ID
                    "comment": this.editPrivilegeVal.comment,   //#备注
                };
                _.trim(data);
                adminAjax.put({
                    url : 'http://hfdns-test.ipo.com/admin/privileges/' + this.modifyPrivilege.id,
                    data : data,
                    success : function () {
                        Toast.success('修改成功');
                        var cloneDtata = _.clone(data);
                        for (let key in cloneDtata) that.tablePrivilegeData[that.modifyPrivilege.index][key] = cloneDtata[key];
                        _.para(that.tablePrivilegeData[that.modifyPrivilege.index], {
                            resource_type : that.searchPrivilegeData.resource_type.display,
                            operation : that.searchPrivilegeData.operation.display,
                        });
                    
                    }
                });
                this.$refs.editDialogPrivilege.hide();
            },
        
            // 删除权限
            delPrivilege (index) {
                var that = this;
                Alert.confirm('确定要删除id是' + index + '的权限吗？', function () {
                    adminAjax.delete({
                        url : 'http://hfdns-test.ipo.com/admin/privileges/' + index,
                        success : function () {
                            that.tablePrivilegeData.splice(that.tablePrivilegeData.indexOf(_.getObj(that.tablePrivilegeData, 'id', index, true)), 1);
                            Toast.success('删除成功');
                        }
                    });
                });
            },
            privPageTo (index){
                this.searchData('searchPrivilegeData', index);
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
                        var val = 1111;
                        that.tablePrivilegeData.forEach(function (item, index, arr) {
                        // item.operation = ys[item.operation];
                            item.select = {
                                value: val++,
                                checked: true
                            };
                        });
                        // 初始页数
                        var total = pageNub(response.data.total);
                        self.$refs.privPagination.setPage(total, response.data.current_page);
                        fn && fn();
                    }
                });
            },
            searchData,
            relation
        }
    }
</script>