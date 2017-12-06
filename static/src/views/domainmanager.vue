<template>
    <div class="page-wrap">
        <div class="grid-search-form" v-if="!isForward">
            <input 
                class="search-item"
                type="text" 
                :placeholder="value.name" 
                v-model="searchRecordData[key].value" 
                v-for="(value, key, index) in searchRecordData" 
                :test="value['type']" v-if="value['type']=='text'"
            />
            <select v-model="searchRecordData[key].value" v-else class="search-item">
                <option v-for="(item, i) in value.display" :value="item.label ? item.value : item">{{item.label ? item.label : item}}</option>
            </select>
            <btn @click="searchData">搜索</btn>
            <btn @click="resetData">重置</btn>
        </div>
        <box title="域名">
            <btn @click="addRecord" style="margin-bottom: 10px;" v-if="!isForward">添加</btn>
            <template v-if="isForward">
                <div>Forward类型域名：当前域名为 Forward类型 域名， 已被forward至&nbsp;&nbsp;<span style="color:red; font-weight:bold;font-size: 20px;">{{forWardIps}}</span>&nbsp;&nbsp;解析 ！！</div>
            </template>
            <template v-else>
                <grid :head="gridColumn" :data="gridData" @callback:deleteRecord="deleteRecord" :colspan="8">
                    <div :slot="'cell:option_'+i" v-for="(item,i) in gridData" class="opt-column">
                        <btn size="small" @click="editRecord(i)" v-show="item.can_update">编辑</btn>
                        <btn @click="deleteRecord(item)" type="danger" size="small" v-show="item.can_delete">删除</btn>
                    </div>
                </grid>
                <vp-pager :total="pager.total" :current="pager.current" @to="pageTo" :position="'right'" :volumn="pager.volumn"></vp-pager>
            </template>
        </box>
        <vp-dialog ref="addDialog" @dialog:save="saveRecord" :title="titleName">
           <div class="form-group">
                <label>主机记录</label>
                <input type="text" class="form-control" v-model="record.host" v-valid="{required:true}" group="innerManger">
            </div>
            <div class="form-group">
                <label>类型</label>
                <select class="form-control" v-model="record.record_type" v-valid="{required:true}" group="innerManger">
                    <option value="A">A</option>
                    <option value="CNAME">CNAME</option>
                    <option value="PTR">PTR</option>
                    <option value="NS">NS</option>
                </select>
            </div>
            <div class="form-group">
              <label>记录值</label>
              <input type="text" class="form-control" v-model="record.value" v-valid="{required:true,ip:ip}" group="innerManger">
            </div>
            <div class="form-group">
              <label>TTL</label>
                <select class="form-control" v-model="record.ttl" v-valid="{required:true}" group="innerManger">
                    <option value="600">600</option>
                    <option value="1800">1800</option>
                    <option value="3600">3600</option>
                </select>
            </div>
            <div class="form-group">
              <label>线路类型</label>
                  <select class="form-control" v-model="record.view_name" v-valid="{required:true}" group="innerManger">
                        <option value="default">default</option>
                        <option :value="item" v-for="(item, i) in searchRecordData.view_name.display">{{item}}</option>
                  </select>
            </div>
            <div class="form-group">
              <label>备注</label>
              <input type="text" class="form-control" v-model="record.comment" v-valid="{required:true}" group="innerManger">
            </div>
        </vp-dialog>
    </div>
</template>
<script>
import box from './index/cmp/box.vue';
import dialog from './_complex/dialog.vue';
import { Datagrid,Pager,Button, Valid, Alert, Toast } from 'vpui';
import Ajax from 'ajax';
import _ from '../components/fn/tool';
import dnsData from './dnsData';

let domainmanager = dnsData('domainmanager');
let domainmanagerUrl = dnsData('url');
let dnsAjax = new Ajax();

export default{
    data (){
        return {
            addOrEdit : '',
            isForward: '',
            // 弹窗标题
            titleName : '',
            // forward的时候的文本
            forWardIps: '',
            // 一条记录
            record : sReset(domainmanager.recordEmpty),
            // 表头
            gridColumn: domainmanager.gridColumn,
            // 表体
            gridData: [],
            // 分页
            pager: domainmanager.pager,
            // 搜索框
            searchRecordData: sReset(domainmanager.searchRecordDataEmpty),
        }
    },
    components: {
        grid: Datagrid,
        vpDialog: dialog,
        vpPager: Pager,
        btn: Button,
        Alert : Alert,
        box,
    },
    directives: {
        "valid":Valid,
    },
    activated(){
        sInit(this);
    },
    watch: {
        '$route.params.zoneId' : function() {
            sInit(this);
        }
    },
    methods: {
        // 添加记录
        addRecord(){
            sAdd(this);
        },
        // 编辑记录
        editRecord(index){
            sEdit(this, {
                isEditLogic : [index]
            });
        },
        // 删除记录
        deleteRecord(record){
            delNoice(this, record.id);
        },
        // 分页
        pageTo(index){
            getTableList(this, {
                zone_id : this.$route.params.zoneId,
                currentPage : index
            });
        },
        // 保存记录
        saveRecord(){
            if (!validInner(this)) return;
            isAddOrEdit(this.addOrEdit) ? editSave(this) : addSave(this);
        },
        // ip验证
        ip () {
            return /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/.test(this.record.value);
        },
        // 搜索
        searchData () {
            getTableList(this, Object.assign(req(this), {
                zone_id : this.$route.params.zoneId
            }));
        },
        // 重置
        resetData () {
            this.searchRecordData = sReset(domainmanager.searchRecordDataEmpty);
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
this.isForward----展示表格还是展示forward
*/
var sAdd = _.decorate(function isAddActive () {
    this.addOrEdit = 0;
});
var sEdit = _.decorate(function isEditActive () {
    this.addOrEdit = 1;
});
var sShowForward = _.decorate(function isForwardActive () {
    this.isForward = true;
});
var sShowTable = _.decorate(function isTableActive () {
    this.isForward = false;
});

// 初始状态
var sInit = function (that) {
    getTableList(that, {
        zone_id : that.$route.params.zoneId
    });
    getLineType(that, that.$route.params.zoneId);
    // 添加记录
    sAdd.add(function isAddLogic() {
        this.titleName = '创建记录';
        this.$vform['innerManger'].resetStyle();
        this.record = sReset(domainmanager.recordEmpty);
        this.$refs.addDialog.show();
    });
    // 编辑记录
    sEdit.add(function isEditLogic(index) {
        this.titleName = '修改记录';
        this.$vform['innerManger'].resetStyle();
        this.$refs.addDialog.show();
        this.record = _.clone(this.gridData[index]);
    });
    // forward展示
    sShowForward.add(function isForwardLogic (response) {
        this.forWardIps = response.data.forwarders;
    });
    // 表格展示
    sShowTable.add(function isTableLogic (data) {
        var that = this;
        dnsAjax.get({
            url: domainmanagerUrl.record,
            data: data,
            success(response){
                that.gridData = response.data.records;
                that.pager.total = Math.ceil(response.data.total / that.pager.volumn);
            }
        });
    });
};

// 重置状态
var sReset = function (data) {
    return JSON.parse(JSON.stringify(data));
};

// 各种不爽的分支
var isForward = function (data) {
    return data == 'forward only';
};
var whichLineType = function (data) {
    return Array.isArray(data);
};
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
        url: domainmanagerUrl.zone + '/' + data.zone_id,
        success(response){
            isForward(response.data.zone_type) ? sShowForward(that, {
                isForwardLogic : [response]
            }) : sShowTable(that, {
                isTableLogic : [data]
            });
        }
    });
};
// 获取线路类型
var getLineType = function (that, zoneId) {
    dnsAjax.get({
        url: domainmanagerUrl.view,
        data : {
            zone_id : zoneId
        },
        success (response) {
            var viewName = that.searchRecordData.view_name;
            viewName.display = [];
            if (whichLineType(response.data)) {
                viewName.display = response.data;
                that.record.view_name = viewName.display[0];
            } else {
                response.data.views.forEach((item) => {
                    viewName.display.push(item.name);
                });
                that.record.view_name = viewName.display[0];
            }
        }
    });
};
// 编辑保存
var editSave = function (that) {
    _.trim(that.record);
    dnsAjax.put({
        url: domainmanagerUrl.record + '/' + that.record.id,
        data: {
            ...that.record,
        },
        success(){
            Alert('修改成功');
            that.$refs.addDialog.hide();
            getTableList(that, {
                zone_id : that.$route.params.zoneId
            });
        }
    });
};
// 添加保存
var addSave = function (that) {
    _.trim(that.record);
    dnsAjax.post({
        url: domainmanagerUrl.record,
        data: {
            ...that.record,
            zone_id : that.$route.params.zoneId
        },
        success(){
            Alert('创建成功');
            that.$refs.addDialog.hide();
            getTableList(that, {
                zone_id : that.$route.params.zoneId
            });
        }
    });
};
// 提交
var req = function (that) {
    // 提交数据处理
    var r = {};
    for (let key in that.searchRecordData) r[key] = that.searchRecordData[key].value;
    r = _.compact(r);
    r = _.trim(r);
    return r;
};
// 通知
var delNoice = function (that, id) {
    Alert.confirm('确定要删除id是' + id + '的域名吗？', function () {
        dnsAjax.delete({
            url: domainmanagerUrl.record + '/' + id,
            success(){
                Alert('删除成功！');
                getTableList(that, {
                    zone_id : that.$route.params.zoneId
                });
            }
        });
    });
};
// 验证
var validInner = function (that) {
    let errLen = that.$vform['innerManger'].checkAll().length;
    that.$vform['innerManger'].checkAll();
    return !errLen;
};
</script>