<template>
    <div class="page-wrap">
        <div class="grid-search-form">
            <input 
                class="search-item" 
                type="text" 
                :placeholder="value.name" 
                v-model="searchServerData[key].value" 
                v-for="(value, key, index) in searchServerData" 
                :test="value['type']" v-if="value['type']=='text'">
            <select class="search-item"  v-model="searchServerData[key].value" v-else>
                <option v-for="(item, i) in value.display" :value="item.label ? item.value : item">{{item.label ? item.label : item }}</option>
            </select>
            <btn @click="searchData">搜索</btn>
            <btn @click="resetData">重置</btn>
        </div>
        <box title="DNS服务器">
            <btn @click="addRecord" v-if="can_add_server" style="margin-bottom: 10px;">添加</btn>
            <btn @click="addBind" v-if="can_add_server" style="margin-bottom: 10px;">编辑BIND主配置文件</btn>
            <grid :head="gridColumn" :data="gridData" @callback:deleteRecord="deleteRecord" @callback:editRecord="editRecord" style="margin-bottom: 10px;" :colspan="6">
                <textarea :slot="'cell:acl_'+i" v-for="(item,i) in gridData" v-html="item.acl" disabled="disabled"></textarea>
                <div :slot="'cell:option_'+i" v-for="(item,i) in gridData" class="opt-column">
                   <btn size="small" @click="editRecord(item)" v-show="item.can_update">编辑</btn>
                   <btn @click="deleteRecord(item)" type="danger" size="small" v-show="item.can_delete">删除</btn>
                </div>
            </grid>
            <vp-pager :total="pager.total" :current="pager.current" @to="pageTo" :position="'right'" :volumn="pager.volumn"></vp-pager>
        </box>
        <vp-dialog ref="addDialog" @dialog:save="saveRecord" :title="titleName">
            <div class="modal-body clearfix">
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>主机名</label>
                    <input type="text" class="form-control" v-model="newServer.host" v-valid="{required:true}" group="dnsServer">
                </div>
                <div class="form-group" style="width: 50%;float:left">
                    <label>IP地址</label>
                    <input type="text" class="form-control" v-model="newServer.ip" v-valid="{required:true}" group="dnsServer">
                </div>
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>环境</label>
                    <select id="s_env" class="form-control" v-model="newServer.env" v-valid="{required:true}" group="dnsServer">
                        <option value="dev">dev</option>
                        <option value="anhouse">anhouse</option>
                        <option value="ga">ga</option>
                    </select>
                </div>
                <div class="form-group" style="width: 50%;float:left">
                    <label>DNS类型</label>
                    <select id="s_type" class="form-control" v-model="newServer.dns_server_type" v-valid="{required:true}" group="dnsServer">
                        <option value="master">master</option>
                        <option value="salve">salve</option>
                    </select>
                </div>
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                <label>进程Itemid</label>
                    <input type="text" class="form-control"  v-model="newServer.zb_process_itemid" v-valid="{required:true}" group="dnsServer">
                    </div>
                <div class="form-group" style="width: 50%;float:left">
                    <label>端口Itemid</label>
                    <input type="text" class="form-control" v-model="newServer.zb_port_itemid" v-valid="{required:true}" group="dnsServer">
                </div>
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>解析Itemid</label>
                    <input type="text" class="form-control" v-model="newServer.zb_resolve_itemid" v-valid="{required:true}" group="dnsServer">
                </div>
                <div class="form-group" style="width: 50%;float:left">
                    <label>解析量Itemid</label>
                    <input type="text" class="form-control" v-model="newServer.zb_resolve_rate_itemid" v-valid="{required:true}" group="dnsServer">
                </div>
            </div>
        </vp-dialog>
        <!-- 编辑BIND主配置文件对话框 -->
        <vp-dialog ref="bindDialog" @dialog:save="saveRecord" :title="'BIND主配置文件'">
            <div class="form-group">
                <lta :rows="5" ref="lineTextArea">
                    <textarea v-model="bindFileData" class="domain-setting-area" rows="5" @input="changeText" v-valid="{required:true}" group="bf"></textarea>
                </lta>
            </div>
        </vp-dialog>
    </div>
</template>
<script>
import box from './index/cmp/box.vue';
import dialog from './_complex/dialog.vue';
import lta from './_complex/lineTextArea.vue';
import { Datagrid,Pager, Toast, Button, Valid, Alert} from 'vpui';
import Ajax from 'ajax';
import _ from '../components/fn/tool';
import dnsData from './dnsData';

let dnsAjax = new Ajax();
let dnsServerData = dnsData('dnsServer');
let dnsServerDataUrl = dnsData('url');

export default{
    data (){
        return {
            addOrEditOrBind : '',
            // bind数据
            bindFileData : '',
            // 权限控制
            can_add_server : '',
            // 弹窗标题
            titleName : '',
            // 表头
            gridColumn: dnsServerData.gridColumn,
            // 表体
            gridData: [],
            // 分页
            pager: dnsServerData.pager,
            // 新的服务器
            newServer: sReset(dnsServerData.newServerEmpty),
            // 搜索框
            searchServerData: sReset(dnsServerData.searchServerDataEmpty),
        }
    },
    components: {
        grid: Datagrid,
        vpDialog: dialog,
        vpPager: Pager,
        btn: Button,
        Alert,
        lta,
        box,
    },
    directives: {
        "valid":Valid,
    },
    mounted(){
        // 获取添加按钮的显示状态
        this.can_add_server = JSON.parse(localStorage.user_info).can_add_server;
        sInit(this);
    },
    methods: {
        // textare实时动作
        changeText(text){
            this.$refs.lineTextArea.setLine(this.bindFileData.match(/\n/g));
        },
        // 添加服务器
        addRecord(){
            sAdd(this);
        },
        // 编辑服务器
        editRecord(record){
            sEdit(this, {
                isEditLogic : [record]
            });
        },
        // 编辑BIND主配置文件
        addBind() {
            sBIND(this);
        },
        // 删除服务器
        deleteRecord(record){
            delNoice(this, record.id);
        },
        // 分页
        pageTo(index){
            getTableList(this, {
                currentPage : index,
            });
        },
        // 保存编辑
        saveRecord(){
            if (!validNDS(this)) return;
            [addSave, editSave, bindSave][this.addOrEditOrBind](this);
        },
        // 搜索
        searchData () {
            getTableList(this, req(this));
        },
        // 重置
        resetData () {
            this.searchServerData = sReset(dnsServerData.searchServerDataEmpty);
        }
    }
}


/*
    状态
*/

// 当前状态
/*
this.addOrEditOrBind----编辑操作还是添加操作
0----添加
1----编辑
2----BIND
*/
var sAdd = _.decorate(function isAddActive () {
    this.addOrEditOrBind = 0;
});
var sEdit = _.decorate(function isEditActive () {
    this.addOrEditOrBind = 1;
});
var sBIND = _.decorate(function isBINDActive () {
    this.addOrEditOrBind = 2;
});

// 初始状态
var sInit = function (that) {
    getTableList(that);
    // 添加dns
    sAdd.add(function isAddLogic () {
        this.titleName = '创建服务器';
        this.$vform['dnsServer'].resetStyle();
        this.newServer = sReset(dnsServerData.newServerEmpty);
        this.$refs.addDialog.show();
    });
    // 编辑dns
    sEdit.add(function isEditLogic (record) {
        this.titleName = '修改服务器';
        this.$vform['dnsServer'].resetStyle();
        this.newServer = _.clone(record);
        this.$refs.addDialog.show();
    });
    // 编辑BIND
    sBIND.add(function isBINDLogic () {
        editBind(this);
    });
};

// 重置状态
var sReset = function (data) {
    return JSON.parse(JSON.stringify(data));
};

// ajax
// 获取表格数据
var getTableList = function (that, data) {
    var obj = {
        pageSize : 10,
        currentPage : 1,
    };
    data ? Object.assign(obj, data) : obj;
    dnsAjax.get({
        url: dnsServerDataUrl.server,
        data,
        success(response){
            that.gridData = response.data.servers;
            that.pager.total = Math.ceil(response.data.total / that.pager.volumn);
        }
    });
};
// 获取bind
var editBind = function (that, data) {
    dnsAjax.get({
        url : dnsServerDataUrl.bind,
        success (response) {
            that.bindFileData = response.data.bind_conf;
            that.$refs.bindDialog.show();
        }
    });
};
// 编辑保存
var editSave = function (that) {
    _.trim(that.newServer);
    dnsAjax.put({
        url : dnsServerDataUrl.server + '/' + that.newServer.id,
        data: {
            ...that.newServer
        },
        success(){
            Alert('修改成功');
            that.$refs.addDialog.hide();
            getTableList(that);
        }
    });
};
// 添加保存
var addSave = function (that) {
    _.trim(that.newServer);
    dnsAjax.post({
        url : dnsServerDataUrl.server,
        data: {
            ...that.newServer
        },
        success(response){
            if(response.status == 201){
                Alert('创建成功');
                that.$refs.addDialog.hide();
                getTableList(that);
            }
        }
    });
};
// bind保存
var bindSave = function (that) {console.log(2);
    _.trim(that.bindFileData);
    // bind保存
    dnsAjax.post({
        url : dnsServerDataUrl.bind,
        data : {
            bind_conf : that.bindFileData
        },
        success (response) {
            Alert('修改成功')
            that.$refs.bindDialog.hide();
        }
    });
};
// 提交
var req = function (that) {
    // 提交数据处理
    var r = {};
    for (let key in that.searchServerData) r[key] = that.searchServerData[key].value;
    r = _.compact(r);
    r = _.trim(r);
    return r;
};
// 通知
var delNoice = function (that, id) {
    Alert.confirm('确定要删除id是' + id + '的服务器吗？', function () {
        dnsAjax.delete({
            url: dnsServerDataUrl.server + '/' + id,
            success(){
                Alert('删除成功！');
                getTableList(that);
            }
        });
    });
};
// 验证
var validNDS = function (that) {
    let errLen = that.$vform['dnsServer'].checkAll().length;
    that.$vform['dnsServer'].checkAll();
    return !errLen;
};
</script>