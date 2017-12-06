<template>
    <div class="page-wrap">
        <div class="grid-search-form">
            <input 
                class="search-item"
                type="text" 
                :placeholder="value.name" 
                v-model="searchViewData[key].value" 
                v-for="(value, key, index) in searchViewData" 
                :test="value['type']" 
                v-if="value['type']=='text'"
            />
            <select class="search-item" v-model="searchViewData[key].value" v-else>
                <option v-for="(item, i) in value.display" :value="item">{{item}}</option>
            </select>
            <btn @click="searchData">搜索</btn>
            <btn @click="resetData">重置</btn>
        </div>
        <box title="View管理">
            <btn @click="addRecord" v-if="can_add_view" style="margin-bottom: 10px;">添加</btn>
            <grid :head="gridColumn" :data="gridData" @callback:deleteRecord="deleteRecord" style="margin-bottom: 10px;" :colspan="4">
                   <textarea :slot="'cell:acl_'+i" v-for="(item,i) in gridData" v-html="item.acl" disabled="disabled" class="domain-setting-area-column"></textarea>
                   <div :slot="'cell:option_'+i" v-for="(item,i) in gridData" class="opt-column">
                       <btn size="small" @click="editRecord(item.id, i)" v-show="item.can_update">编辑</btn>
                       <btn @click="deleteRecord(item, i)" type="danger" size="small" v-show="item.can_delete">删除</btn>
                   </div>
            </grid>
            <vp-pager :total="pager.total" :current="pager.current" @to="pageTo" :position="'right'" :volumn="pager.volumn"></vp-pager>
        </box>
        <vp-dialog ref="addDialog" @dialog:save="saveRecord" :title="titleName">
           <div class="form-group">
                <label>区域名称</label>
                <input :disabled="titleName == '修改view' && 'disabled'" type="text" class="form-control" v-model="view.name" v-valid="{required:true}" group="viewManger">
            </div>
            <div class="form-group">
                <label>区域名配置</label>
                <line-textarea :rows="5" ref="lineTextArea">
                    <textarea v-model="view.acl" class="domain-setting-area" rows="5" @input="changeText" v-valid="{required:true,ip:ip}" group="viewManger"></textarea>
                </line-textarea>
            </div>
        </vp-dialog>
    </div>
</template>
<script>
import dialog from './_complex/dialog.vue';
import lineTextArea from './_complex/lineTextArea.vue';
import box from './index/cmp/box.vue';
import { Datagrid, Pager, Toast, Button, Valid, Alert } from 'vpui';
import Ajax from 'ajax';
import _ from '../components/fn/tool';
import dnsData from './dnsData';

let dnsAjax = new Ajax();
let viewData = dnsData('view');
let viewDataUrl = dnsData('url');

export default{
    data (){
        return {
            addOrEdit : '',
            // 弹窗标题
            titleName : '',
            // 权限控制
            can_add_view : '',
            // 表头
            gridColumn: viewData.gridColumn,
            // 表体
            gridData: [],
            // 分页
            pager: viewData.pager,
            // 新view
            view:sReset(viewData.emptyView),
            // 搜索框
            searchViewData : sReset(viewData.searchViewDataEmpty)
        }
    },
    components: {
        grid: Datagrid,
        vpDialog: dialog,
        vpPager: Pager,
        btn: Button,
        Alert : Alert,
        lineTextarea: lineTextArea,
        box
    },
    directives: {
        "valid":Valid,
    },
    mounted(){
        // 获取添加按钮的显示状态
        this.can_add_view = JSON.parse(localStorage.user_info).can_add_view;
        sInit(this);
    },

    methods: {
        // 添加view
        addRecord(){
            sAdd(this);
        },
        // 编辑view
        editRecord(id, index){
            sEdit(this, {
                isEditActive : [id],
                isEditLogic : [index]
            });
        },
        // 删除view
        deleteRecord(record, index){
            delNoice(this, record.id, index);
        },
        // 分页
        pageTo(index){
            getTableList(this, {
                currentPage : index,
            });
        },
        // 保存编辑
        saveRecord(){
            if (!validView(this)) return;
            isAddOrEdit(this.addOrEdit) ? editSave(this) : addSave(this);
        },
        // textare实时动作
        changeText(text){
            this.$refs.lineTextArea.setLine(this.view.acl.match(/\n/g));
        },
        // ip验证
        ip () {
            var ex = this.view.acl.match(/[^\n]+/g);
            var result = false;
            if (ex) {
                result = ex.every((item, index, arr) => {
                    return /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])(?:\/\d+)?$/.test(item);
                });
            }
            return result;
        },
        // 搜索
        searchData (str) {
            getTableList(this, req(this));
        },
        // 重置
        resetData () {
            this.searchViewData = sReset(viewData.searchViewDataEmpty);
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
    // 添加view
    sAdd.add(function isAddLogic () {
        this.titleName = '创建view';
        this.$vform['viewManger'].resetStyle();
        this.view = sReset(viewData.emptyView);
        this.$refs.addDialog.show();
    });
    // 编辑view
    sEdit.add(function isEditLogic (index) {
        this.titleName = '修改view';
        this.$vform['viewManger'].resetStyle();
        this.view = _.clone(this.gridData[index]);
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
        url: viewDataUrl.view,
        data,
        success(response){
            that.gridData = response.data.views;
            that.pager.total = Math.ceil(response.data.total / that.pager.volumn);
        }
    });
};
// 添加view
var addSave = function (that, data) {
    _.trim(that.view);
    dnsAjax.post({
        url: viewDataUrl.view,
        data: {
            ...that.view
        },
        success(){
            Toast.success('创建成功');
            that.$refs.addDialog.hide();
            getTableList(that);
        }
    });
};
// 保存view
var editSave = function (that, data) {
    _.trim(that.view);
    dnsAjax.put({
        url: viewDataUrl.view + '/'+ that.view.id,
        data: {
            ...that.view
        },
        success(){
            Alert('修改成功');
            that.$refs.addDialog.hide();
            getTableList(that);
        }
    });
};
// 通知
var delNoice = function (that, id) {
    Alert.confirm('确定要删除id是' + id + '的view吗？', function () {
        dnsAjax.delete({
            url: viewDataUrl.view + '/'+ id,
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
    for (let key in that.searchViewData) r[key] = that.searchViewData[key].value;
    r = _.compact(r);
    r = _.trim(r);
    return r;
};
// 验证
var validView = function (that) {
    let errLen = that.$vform['viewManger'].checkAll().length;
    that.$vform['viewManger'].checkAll();
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
    .domain-setting-area-column{
        margin-top: 12px;
        background-color: #e1e1ea;
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