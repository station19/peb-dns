<template>
    <div class="page-wrap">
        <div class="grid-search-form">
            <input 
                class="search-item" 
                type="text" 
                :placeholder="value.name" 
                v-model="searchLogData[key].value" 
                v-for="(value, key, index) in searchLogData" 
                :test="value['type']" 
                v-if="value['type']=='text'">
            <select class="search-item" v-model="searchLogData[key].value" v-else>
                <option v-for="(item, i) in value.display" :value="item === '全部' ? '' : item">{{item}}</option>
            </select>
            <btn @click="searchData">搜索</btn>
            <btn @click="resetData">重置</btn>
        </div>
        <box title="用户操作记录">
            <vp-grid :head="table_base.col" :data="operationLogs" :colspan="8"></vp-grid>
            <vp-pager :total="pager.total" :current="pager.current" @to="pageTo" :position="'right'" :volumn="pager.volumn"></vp-pager>
        </box>
    </div>
</template>
<script>
import box from './index/cmp/box.vue';
import { Datagrid, Pager, Button } from 'vpui';
import Ajax from 'ajax';
import _ from '../components/fn/tool';
import dnsData from './dnsData';

let logs = dnsData('logs');
let logsUrl = dnsData('url');
let dnsAjax = new Ajax();

export default {
    data () {
        return {
            // 表体
            operationLogs : [],
            // 表头
            table_base: logs.table_base,
            // 分页
            pager: logs.pager,
            // 搜索框
            searchLogData : sReset(logs.searchLogData),
        };
    },
    components:{
        "vp-grid": Datagrid,
        vpPager: Pager,
        btn: Button,
        box: box
    },
    mounted(){
        sInit(this);
    },
    methods : {
        // 分页
        pageTo (index) {
            getTableList(this, {
                currentPage : index,
            });
        },
        // 搜索
        searchData (str) {
            getTableList(this, req(this));
        },
        // 重置
        resetData () {
            this.searchLogData = sReset(logs.searchLogData);
        }
    }
}

/*
    状态
*/
// 初始状态
var sInit = function (that) {
    getTableList(that);
};
// 重置状态
var sReset = function (data) {
    return JSON.parse(JSON.stringify(data));
};

// 页码
var pageNub = function (total) {
    var nub = total / 10;
    return total > 10 ? Math.floor(nub % 2 == 0 ? nub : nub + 1)  : 1;
}
// ajax
// 获取表格
var getTableList = function (that, data) {
    var obj = {
        pageSize : 10,
        currentPage : 1,
    };
    data ? Object.assign(obj, data) : obj;
    dnsAjax.get({
        url : logsUrl.log,
        data : data,
        success : function (response) {
            res(that, response.data);
        }
    });
};
// 提交
var req = function (that) {
    // 提交数据处理
    var r = {};
    for (let key in that.searchLogData) r[key] = that.searchLogData[key].value;
    r = _.compact(r);
    r = _.trim(r);
    return r;
};
// 获取
var res = function (that, data) {
    // 获取数据处理
    that.operationLogs = data.operation_logs;
    // 1. 换行处理
    that.operationLogs.forEach(function (item, index, arr) {
        item.target_detail = item.target_detail.replace(/\n/g, "<br/>");
    });
    // 2. 设置分页
    that.pager.total = pageNub(data.total);
};
</script>