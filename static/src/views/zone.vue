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
            <btn @click="">重置</btn>
        </div>
        <box title="ZONE管理">
            <div style="margin-bottom: 10px;">
                <btn @click="showWindow" v-if="can_add_zone">添加</btn>
                <span style="color: red;margin-left: 20px;" v-if="can_add_zone">警示！！添加新zone，或者已有zone关联新的view时，请记得添加master的A记录，否则会reload失败！！！
                </span>
            </div>
            <grid :head="gridColumn" :data="gridData" @callback:deleteRecord="deleteRecord" @callback:editRecord="editRecord" style="margin-bottom: 10px;" :colspan="7">
                <span :slot="'cell:zone_group_'+i" v-for="(item,i) in gridData" v-html="zoneGroup[item.zone_group]" ></span>
                <div :slot="'cell:option_'+i" v-for="(item,i) in gridData" class="opt-column">
                    <btn size="small" @click="editRecord(item)" v-show="item.can_update">编辑</btn>
                    <btn @click="deleteRecord(item)" type="danger" size="small" v-show="item.can_delete">删除</btn>
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
import Ajax from 'ajax';
import { zoneGroup } from 'dict';
import lineTextArea from './_complex/lineTextArea.vue';
import dialog from './_complex/dialog.vue';
import _ from '../components/fn/tool';
import box from './index/cmp/box.vue';
    
let _ajax = new Ajax();

let modalEmpty = {
    name : '', 
    view_ids : [],
    forwarders : '',
    zone_type : 'master',
    zone_group : '0'
};
let searchZoneDataEmpty = {
    id : {
        name : 'id',
        value : '',
        type : 'text',
    },
    name : {
        name : '名称',
        value : '',
        type : 'text',
    },
    zone_group : {
        name : '归类',
        value : '',
        display : [{label: '全部', value: ''},'外部', '内部', '劫持'],
        type : 'select',
    },
    zone_type : {
        name : '类型',
        value : '',
        display : [{label: '全部', value: ''},'forword', 'master', 'salve'],
        type : 'select',
    }
};

export default{
    data (){
        return {
            titleName : '',
            can_add_zone : '',
            bb: {
                testA: [],
            },
            domainName: '',
            gridColumn: {
                id: {
                    label: 'ID',
                    width: '80px'
                },
                name: 'ZONE',
                zone_group: {
                    label: '域名归类'
                },
                zone_type: '域名类别',
                view_name_list_string: '关联区域',
                forwarders :'转发域名IP地址',
                option: {
                    type: 'action',
                    label: '操作',
                    width: '130px'
                }
            },
            gridData: [],
            pager: {
                current: 1,
                total: 0,
                volumn: 10
            },
            modal:JSON.parse(JSON.stringify(modalEmpty)),
            viewList: [],
            zoneGroup: zoneGroup,
            searchZoneDataEmpty,
            searchZoneData : JSON.parse(JSON.stringify(searchZoneDataEmpty)),
            // 区域关联实时更新
            timer : ''
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
        let self = this;
        let zoneId = self.$route.params.zoneId;
        self.fetchRecords(zoneId);
        this.areaList();
        // 获取添加按钮的显示状态
        this.can_add_zone = JSON.parse(localStorage.user_info).can_add_zone;
    },
    methods: {
        areaList () {
            var self = this;
            // 区域关联
            _ajax.get({
                url: 'http://hfdns-test.ipo.com/dns/views',
                data: {
                    currentPage: 1
                },
                success(response){
                    response.data.views.forEach((view) => {
                        self.viewList.push({value: view.id, text: view.name})
                    });
                }
            });
        },
        validZone () {
            let errLen = this.$vform['zoneManger'].checkAll().length;
            this.$vform['zoneManger'].checkAll();
            // !errLen && Alert('验证通过，发送请求', true);
            return !errLen;
        },
        showWindow(){
            this.areaList();
            this.titleName = '创建ZONE';
            this.$vform['zoneManger'].resetStyle();
            this.modal = JSON.parse(JSON.stringify(modalEmpty));
            this.$refs.addDialog.show();
        },
        deleteRecord(record){
            let id = record.id;
            let self = this;
            Alert.confirm('确定要删除id是' + id + '的ZONE吗？', function () {
                _ajax.delete({
                    url: 'http://hfdns-test.ipo.com/dns/zones/'+ id,
                    success(){
                        Toast.success('删除成功！');
                        let target = null;
                        self.gridData.forEach((item,index) => {
                            if(item.id == id){
                                target = index;
                            }
                        });
                        self.gridData.splice(target, 1);
                    }
                });
            });
        },
        pageTo(index){
            this.pager.current = index;
            this.fetchRecords();
        },
        saveRecord(){
            if (!this.validZone()) return;
            let self = this;
            let url = 'http://hfdns-test.ipo.com/dns/zones';
            _.trim(self.modal);
            // 编辑
            if(self.modal.id){
                url += '/'+self.modal.id;
                _ajax.put({
                    url,
                    data: {
                        ...self.modal
                    },
                    success(){
                        Alert('修改成功');
                        self.$refs.addDialog.hide();
                        self.fetchRecords();
                    }
                });
                return;
            }
            // 添加
            _ajax.post({
                url,
                data: {
                    ...self.modal
                },
                success(response){
                    if(response.status == 201){
                        Alert('创建成功');
                        self.$refs.addDialog.hide();
                        self.fetchRecords();
                        // 刷新侧边栏
                        self.$parent.$parent.resetSidebar();
                    }
                }
            });
        },
        fetchRecords(){
            let self = this;
            _ajax.get({
                url: 'http://hfdns-test.ipo.com/dns/zones',
                data: {
                    pageSize: 10,
                    currentPage: this.pager.current
                },
                success(response){
                    response.data.zones.forEach((item, index, arr) => {
                        item.view_name_list_string = JSON.parse(item.view_name_list.replace(/'/g, '"')).join(',');
                        // 处理域名分号变换行
                        item.forwarders = item.forwarders.replace(/\s/g, '').replace(/;/g, '\n');
                    });
                    console.log(response.data.zones);
                    self.gridData = response.data.zones;
                    let pageTotal = Math.ceil(response.data.total / self.pager.volumn);
                    self.pager.total = pageTotal;
                }
            });
        },
        editRecord(record){
            this.titleName = '修改ZONE';
            this.$vform['zoneManger'].resetStyle();
            this.modal = _.clone(record);
            this.$refs.addDialog.show();
        },
        changeText(text){
            this.$refs.lineTextArea.setLine(this.modal.forwarders.match(/\n/g));
        },
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
        searchData () {
            var reqData = {};
            for (var key in this.searchZoneData) {
                reqData[key] = this.searchZoneData[key].value;
            }
            var self = this;
            reqData = _.compact(reqData);
            reqData = _.para(reqData, {
                zone_group : _.invert(self.searchZoneData.zone_group.display)
            });
            self.viewList = [];
            _.trim(reqData);
            _ajax.get({
                url: 'http://hfdns-test.ipo.com/dns/zones',
                data: reqData,
                success(response){
                    self.gridData = response.data.zones;
                    let pageTotal = Math.ceil(response.data.total / self.pager.volumn);
                    self.pager.total = pageTotal;
                }
            });

        },
        // 域名验证
        reDomainName () {
            return /^(?=^.{3,255}$)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$/.test(this.modal.name);
        }
    }
}
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