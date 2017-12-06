<template>
    <div class="page-wrap">
        <div class="grid-search-form">
            <input 
                class="search-item"
                type="text" 
                :placeholder="value.name" 
                v-model="searchZoneData[key].value" 
                v-for="(value, key, index) in searchZoneData" 
                :test="value['type']" v-if="value['type']=='text'">
            <select class="search-item" v-model="searchZoneData[key].value" v-else>
                <option v-for="(item, i) in value.display" :value="item.label? item.value : item">{{item.label?item.label:item}}</option>
            </select>
            <btn @click="searchData">搜索</btn>
            <btn @click="resetData">重置</btn>
        </div>
        <box title="ZONE管理">
            <div style="margin-bottom: 10px;">
                <btn @click="addZone" v-if="can_add_zone">添加</btn>
                <span style="color: red;margin-left: 20px;" v-if="can_add_zone">警示！！添加新zone，或者已有zone关联新的view时，请记得添加master的A记录，否则会reload失败！！！
                </span>
            </div>
            <grid :head="gridColumn" :data="gridData" @callback:deleteRecord="deleteRecord" @callback:editRecord="editRecord" style="margin-bottom: 10px;" :colspan="7">
                <span :slot="'cell:zone_group_'+i" v-for="(item,i) in gridData" v-html="zoneGroup[item.zone_group]" ></span>
                <div :slot="'cell:option_'+i" v-for="(item,i) in gridData" class="opt-column">
                    <btn size="small" @click="editRecord(item)" v-show="item.can_update">编辑</btn>
                    <btn @click="deleteRecord(item, i)" type="danger" size="small" v-show="item.can_delete">删除</btn>
                </div>
            </grid>
            <vp-pager :total="pager.total" :current="pager.current" @to="pageTo" :position="'right'" :volumn="pager.volumn"></vp-pager>
        </box>
        <vp-dialog ref="addDialog" @dialog:save="saveRecord" :title="titleName">
            <div class="modal-body clearfix">
                <div class="form-group">
                    <label>域名</label>
                    <input :disabled="titleName == '修改ZONE' && 'disabled'" type="text" class="form-control" v-model="modal.name" v-valid="{required:true,reDomainName:reDomainName}" group="zoneManger">
                </div>
                <div class="form-group" v-if="modal.zone_group != 0">
                    <label>关联区域</label>
                    <vp-select width="535" type="multiple" :options="viewList" v-model="modal.view_ids" v-valid="{required:true}" group="zoneManger"></vp-select>
                </div>
                <div class="form-group" v-if="modal.zone_group != 0">
                    <label>域名类别</label>
                    <select :disabled="titleName == '修改ZONE' && 'disabled'" id="s_env" class="form-control" v-model="modal.zone_type" v-valid="{required:true}" group="zoneManger">
                        <option value="master">主域名</option>
                        <option value="forward only">转发域名</option>
                    </select>
                </div>
                <div class="form-group" v-if="modal.zone_type == 'forward only'">
                    <label>转发域名IP地址</label>
                    <line-textarea :rows="5" ref="lineTextArea">
                        <textarea v-model="modal.forwarders" class="domain-setting-area" rows="5" @input="changeText" v-valid="{required:true,ip:ip}" group="zoneManger">
                        </textarea>
                    </line-textarea>
                </div>
                <div class="form-group">
                    <label>域名归类</label>
                    <select class="form-control" v-model="modal.zone_group" v-valid="{required:true}" group="zoneManger">
                        <option v-for="key in Object.keys(zoneGroup)" :value="key">{{zoneGroup[key]}}</option>
                    </select>
                </div>
            </div>
        </vp-dialog>
    </div>
</template>
<script>
import { Datagrid, Pager, Button, Select, Valid, Alert} from 'vpui';
import lineTextArea from './_complex/lineTextArea.vue';
import dialog from './_complex/dialog.vue';
import box from './index/cmp/box.vue';
import { zoneGroup } from 'dict';
import Ajax from 'ajax';
import _ from '../components/fn/tool';
import dnsData from './dnsData';

let dnsAjax = new Ajax();
let zoneData = dnsData('zone');
let zoneDataUrl = dnsData('url');

export default{
    data (){
        return {
            addOrEdit : '',
            // 弹窗标题
            titleName : '',
            // 权限控制
            can_add_zone : '',
            // 表头
            gridColumn: zoneData.gridColumn,
            // 表体
            gridData: [],
            // 分页
            pager: zoneData.pager,
            // 编辑的zone
            modal:sReset(zoneData.modalEmpty),
            // 区域列表
            viewList: [],
            // 域名类型
            zoneGroup: zoneGroup,
            // 搜索框
            searchZoneData : sReset(zoneData.searchZoneDataEmpty),
        }
    },
    components: {
        grid: Datagrid,
        vpDialog: dialog,
        vpPager: Pager,
        btn: Button,
        vpSelect: Select,
        lineTextarea: lineTextArea,
        Alert,
        box
    },
    directives: {
        "valid":Valid,
    },
    mounted(){
        // 获取添加按钮的显示状态
        this.can_add_zone = JSON.parse(localStorage.user_info).can_add_zone;
        sInit(this);
    },
    methods: {
        // 添加zone
        addZone(){
            sAdd(this);
        },
        // 编辑zone
        editRecord(record){
            sEdit(this, {
                isEditLogic : [record],
            });
        },
        // 删除zone
        deleteRecord(record, index){
            delNoice(this, record.id, index);
        },
        // 分页
        pageTo(index){
            getTableList(that, {
                currentPage : index
            });
        },
        // 保存zone
        saveRecord(){
            if (!validZone(this)) return;
            isAddOrEdit(this.addOrEdit) ? editSave(this) : addSave(this);
        },
        // textare实时动作
        changeText(text){
            this.$refs.lineTextArea.setLine(this.modal.forwarders.match(/\n/g));
        },
        // ip验证
        ip () {
            var ex = this.modal.forwarders.match(/[^\n]+/g);
            var result = false;
            if (ex) {
                result = ex.every((item, index, arr) => {
                    return /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/.test(item);
                });
            }
            return result;
        },
        // 搜索
        searchData () {
            getTableList(this, req(this));
        },
        // 域名验证
        reDomainName () {
            return /^(?=^.{3,255}$)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$/.test(this.modal.name);
        },
        // 重置
        resetData () {
            this.searchZoneData = sReset(zoneData.searchZoneDataEmpty);
        }
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

// 初始状态
var sInit = function (that) {
    getTableList(that);
    getAreaList(that);
    // 添加ZONE
    sAdd.add(function isAddLogic () {
        getAreaList(this);
        this.titleName = '创建ZONE';
        this.$vform['zoneManger'].resetStyle();
        this.modal = sReset(zoneData.modalEmpty);
        this.$refs.addDialog.show();
    });
    // 编辑ZONE
    sEdit.add(function isEditLogic (record) {
        this.titleName = '修改ZONE';
        this.$vform['zoneManger'].resetStyle();
        this.modal = _.clone(record);
        this.$refs.addDialog.show();
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
        url: zoneDataUrl.zone,
        data,
        success(response){
            response.data.zones.forEach((item, index, arr) => {
                item.view_name_list_string = JSON.parse(item.view_name_list.replace(/'/g, '"')).join(',');
                // 处理域名分号变换行
                item.forwarders = item.forwarders.replace(/\s/g, '').replace(/;/g, '\n');
            });
            that.gridData = response.data.zones;
            that.pager.total = Math.ceil(response.data.total / that.pager.volumn);
        }
    });
};
// 区域关联
var getAreaList = function (that, data) {
    // 重置区域
    that.viewList = [];
    dnsAjax.get({
        url: zoneDataUrl.view,
        data: {
            currentPage: 1
        },
        success(response){
            response.data.views.forEach((view) => {
                that.viewList.push({value: view.id, text: view.name})
            });
        }
    });
};
// 编辑保存
var editSave = function (that, data) {
    _.trim(that.modal);
    dnsAjax.put({
        url : zoneDataUrl.zone + '/' + that.modal.id,
        data: {
            ...that.modal
        },
        success(){
            Alert('修改成功');
            that.$refs.addDialog.hide();
            getTableList(that);
        }
    });
};
// 添加保存
var addSave = function (that, data) {
    _.trim(that.modal);
    dnsAjax.post({
        url : zoneDataUrl.zone,
        data: {
            ...that.modal
        },
        success(response){
            if(response.status == 201){
                Alert('创建成功');
                that.$refs.addDialog.hide();
                getTableList(that);
                // 刷新侧边栏
                that.$parent.$parent.resetSidebar();
            }
        }
    });
};
// 通知
var delNoice = function (that, id) {
    Alert.confirm('确定要删除id是' + id + '的ZONE吗？', function () {
        dnsAjax.delete({
            url: zoneDataUrl.zone + '/' + id,
            success(){
                Alert('删除成功！');
                getTableList(that);
            }
        });
    });
};
// 提交
var req = function (that) {
    // 提交数据处理
    var r = {};
    for (let key in that.searchZoneData) r[key] = that.searchZoneData[key].value;
    r = _.compact(r);
    r = _.para(r, {
        zone_group : _.invert((that.searchZoneData.zone_group.display.slice(1)))
    });
    r = _.trim(r);
    return r;
};
// 验证
var validZone = function (that) {
    let errLen = that.$vform['zoneManger'].checkAll().length;
    that.$vform['zoneManger'].checkAll();
    return !errLen;
};



</script>
<style scoped lang="less">
.box-primary .box-header+.search{
    margin:10px;
}
    .row {
        margin: 0;
    }
    .add-btn{
        float: right;
       /* margin-right: 60px;*/
    }
    .box-body{
        padding-top: 0;
    }
    .pager-wrap{
        position: fixed;
        bottom: 2px;
        right: 33px;
        background-color: #fff;
    }
    .lg-pager{
      margin: 0;
    }
    .domain-setting-area{
        background: #000;
        color: #fff;
        line-height: 1.5;
        padding: 10px;
        /*margin-top: 15px;*/
        height: 200px;
    }
    .search{
        display:flex;
        margin-bottom:20px;
        >*{
            margin:3px;
            
        }
        >input{
            flex:1;
            line-height:36px;
            height:38px;
        }
        >select{
            flex:1;
            line-height:36px;
            height:38px;
        }
        >button{
            font-size:14px;
            flex:1;
            line-height:36px;
            height:38px;
        }
    }
</style>