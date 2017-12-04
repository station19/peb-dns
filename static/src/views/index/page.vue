<template>
    <div class="page-wrap">
        <counter-warp></counter-warp>
        <waterfall class="content-wrap" :column="1">
            <item>
                <box title="服务器解析量" id="serverParse">
                    <div style="position:absolute;right: 68px; z-index: 1000">
                    <vp-select v-model="val" :options="list" @select="select1"></vp-select>
                    </div>
                    <div id="echarts1"></div>
                </box>
            </item>
            <item>
                <box title="服务器状态">
                    <div class="row">
                        <div class="col-md-3 serverStatus">
                            <div class="snow" v-for="(state, index) in serversState" :class="{no: !state.active, yes:state.active}">
                                <h4 class="serverStatusName">{{state.active ? 'online' : '异常'}}</h4>
                                <h4 class="serverHost">{{state.name}}</h4>
                                <ul class="serverStatusList">
                                    <li><span class="normal" :class="state.state.process"></span><span>进程</span></li>
                                    <li><span class="normal" :class="state.state.port"></span><span>端口</span></li>
                                    <li><span class="normal" :class="state.state.resolve"></span><span>解析</span></li>
                                </ul>
                            </div>
                            <div class="snow add" v-if="can_add_server">
                                <h4>添加新的服务器</h4>
                                <div @click="addRecord">添加</div>
                            </div>
                        </div>
                    </div>
                </box>
            </item>
            <item>
                <box title="用户操作记录">
                    <vp-grid :head="table_base.col" :data="operationLogs" :colspan="table_base.colspan"></vp-grid>
                    <vp-pager :total="pager.total" :current="pager.current" @to="pageTo" :position="'right'" :volumn="pager.volumn"></vp-pager>
                </box>
            </item>
        </waterfall>
        <vp-dialog ref="addDialog" title="创建DNS服务器" @dialog:save="createDNS">
            <div class="modal-body clearfix">
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>主机名</label>
                    <input type="text" class="form-control" v-model="newServer.host" v-valid="{required:true}" group="newServer">
                </div>
                <div class="form-group" style="width: 50%;float:left">
                    <label>IP地址</label>
                    <input type="text" class="form-control" v-model="newServer.ip" v-valid="{required:true}" group="newServer">
                </div>
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>环境</label>
                    <select id="s_env" class="form-control" v-model="newServer.env" v-valid="{required:true}" group="newServer">
                        <option value="dev">dev</option>
                        <option value="anhouse">anhouse</option>
                        <option value="ga">ga</option>
                    </select>
                </div>
                <div class="form-group" style="width: 50%;float:left">
                    <label>DNS类型</label>
                    <select id="s_type" class="form-control" v-model="newServer.dns_server_type" v-valid="{required:true}" group="newServer">
                        <option value="master">master</option>
                        <option value="salve">salve</option>
                    </select>
                </div>
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                <label>进程Itemid</label>
                    <input type="text" class="form-control"  v-model="newServer.zb_process_itemid" v-valid="{required:true}" group="newServer">
                    </div>
                <div class="form-group" style="width: 50%;float:left">
                    <label>端口Itemid</label>
                    <input type="text" class="form-control" v-model="newServer.zb_port_itemid" v-valid="{required:true}" group="newServer">
                </div>
                <div class="form-group" style="width: 48%;float:left;margin-right:10px;">
                    <label>解析Itemid</label>
                    <input type="text" class="form-control" v-model="newServer.zb_resolve_itemid" v-valid="{required:true}" group="newServer">
                </div>
                <div class="form-group" style="width: 50%;float:left">
                    <label>解析量Itemid</label>
                    <input type="text" class="form-control" v-model="newServer.zb_resolve_rate_itemid" v-valid="{required:true}" group="newServer">
                </div>
            </div>
        </vp-dialog>
    </div>
</template>
<script>
    import counterWarp from './cmp/counterWrap.vue';

    import box from './cmp/box.vue';
    import {WaterFallItem, WaterFall, Alert} from 'vpui';
    import Ajax from 'ajax';
    let indexAjax = new Ajax();
    import echarts from 'echarts';
    import { Datagrid,Pager } from 'vpui';

    import dialog from '../_complex/dialog.vue';
    import { Select } from 'vpui';
    import {Toast, Valid, Radio, Checkbox} from 'vpui';
    const arr = new Array(24).fill(true).map((item, i) => ({ value: i * 1 + 1, text: `${ i * 1 + 1 }小时` }));
    export default {
        data(){
            return {
                val: 1,
                option: {},
                list: [...arr],
                serverParse : '',
                serverName : [],
                serverTime : [],// 时期时间
                series : [],//echarts线数据
                serversState : [],//服务器状态
                operationLogs : [],//操作日志
                table_base: {
                    col: {
                        target_detail: {
                            label: '对象详情',
                            width: '500px'
                        },
                        target_type : '对象类型',
                        operation_type: '操作类型',
                        target_name: '对象名称',
                        target_id: '操作对象',
                        operator : '操作者',
                        id : '对象ID',
                        operation_time : '操作时间'
                    },
                },
                newServer : {
                    host : '', 
                    ip : '',
                    env : '',
                    dns_server_type : '',
                    zb_process_itemid : '',
                    zb_port_itemid : '',
                    zb_resolve_itemid : '',
                    zb_resolve_rate_itemid : '',
                },
                // 分页
                pager: {
                    current: 1,
                    total: 10,
                    volumn: 10
                },
                // 折线图线的颜色
                lineColor : ['CornflowerBlue', 'PaleGreen', 'HotPink', 'Gold', 'Cyan', 'Orange', 'LightSalmon', 'FireBrick', 'Violet'],
                // 颜色顺序
                nub : 0,
                // 定时器管理
                timer : '',
                // 获取添加按钮的显示状态
                can_add_server : '',
            };
        },
        directives: {
            "valid":Valid
        },
        mounted(){
            var that = this;
            // 操作日志-1页
            indexAjax.get({
                url : 'http://hfdns-test.ipo.com/dns/oplogs',
                data : {
                    pageSize : 10,
                    currentPage : 1
                },
                success : function (response) {
                    that.operationLogs = response.data.operation_logs;
                    that.pager.total = that.pageNub(response.data.total);
                }
            });
            this.getServer();
            // 获取添加按钮的显示状态
            this.can_add_server = JSON.parse(localStorage.user_info).can_add_server;
        },
        activated(){
            // 30秒重新获取服务器的状态
            this.timer = setInterval(this.getServer, 30000);
        },
        deactivated (){
            clearInterval(this.timer);
        },
        components:{
            box: box,
            waterfall: WaterFall,
            item: WaterFallItem,
            'vp-select' : Select,
            counterWarp: counterWarp,
            "vp-grid": Datagrid,
            vpDialog: dialog,
            vpPager: Pager,
            Alert,
        },
        methods : {
            getServer () {
                var that = this;
                // 服务器接口
                indexAjax.get({
                    url : 'http://hfdns-test.ipo.com/dns/servers',
                    data : {
                        
                    },
                    success : function (response) {
                        // 重置服务器状态
                        that.serversState = [];
                        response.data.servers.forEach(function (item, index, arr) {
                            // 服务器状态
                            indexAjax.get({
                                url : 'http://hfdns-test.ipo.com/page/server_status',
                                data : {
                                    "server_id" : item.id,
                                },
                                success : function (response) {
                                    that.serversState.push(response.data);
                                    var active = Object.keys(response.data).every(function (item, index, arr) {
                                        return response.data[item] == 1;
                                    });
                                    var obj = {};
                                    for (let key in response.data) {
                                        obj[key + 1] = response.data[key] * 1 ? 'online' : '异常';
                                        obj[key] = response.data[key] * 1 ? 'green' : 'red';
                                    }
                                    response.data.state = obj;
                                    // 添加当前状态
                                    response.data.active = active;
                                    // 添加服务器名字
                                    response.data.name = item.host;
                                }
                            });
                        });
                    }
                });
            },
            // 表单验证
            validNewServer () {
                let errLen = this.$vform['newServer'].checkAll().length;
                this.$vform['newServer'].checkAll();
                // !errLen && Toast.success('验证通过，发送请求', true);
                return !errLen;
            },
            // 页码
            pageNub (total) {
                var nub = total / 10;
                return total > 10 ? Math.floor(nub % 2 == 0 ? nub : nub + 1)  : 1;
            },
            // 去第几页
            pageTo (index) {
                var that = this;
                indexAjax.get({
                    url : 'http://hfdns-test.ipo.com/dns/oplogs',
                    data : {
                        pageSize : 10,
                        currentPage : index
                    },
                    success : function (response) {
                        that.operationLogs = response.data.operation_logs;
                    }
                });
            },
            addRecord(){
                this.newServer = {
                    host : '', 
                    ip : '',
                    env : '',
                    dns_server_type : '',
                    zb_process_itemid : '',
                    zb_port_itemid : '',
                    zb_resolve_itemid : '',
                    zb_resolve_rate_itemid : '',
                };
                this.$vform['newServer'].resetStyle();
                this.$refs.addDialog.show();
            },
            select1 (i) {
                var that = this;
                var dt = new Date();
                dt.setHours(dt.getHours() - this.val);
                var time = dt.getTime();
                var c = that.getTime(time);
                c = c.replace(/\s/, '-').replace(/:/, '-');
                c = /(.{16})/.exec(c)[1];



                // 服务器解析量
                indexAjax.get({
                    url : 'http://hfdns-test.ipo.com/page/servers_resolve_rate',
                    data : {
                        "start_time": c,
                        // "end_time": "2016-11-02-14-39"
                    },
                    success : function (response) {
                        that.serverParse = response.data;
                        // 每次请求都清空再来
                        that.serverName = [];
                        that.serverTime = [];
                        that.series = [];
                        // 一个服务器的时间
                        var obj;

                        
                        for (var key in that.serverParse) {
                            obj = that.serverParse[key].data;
                            that.serverName.push(key);
                            that.series.push({
                                name : key,
                                type : 'line',
                                data : (function () {
                                    var result = [];
                                    for (var key2 in that.serverParse[key].data) {
                                        result.push(that.serverParse[key].data[key2]);
                                    }
                                    return result;
                                })(),
                                itemStyle : {
                                    normal : {
                                        // color : that.lineColor[that.nub++],
                                        borderWidth : 7
                                    } 
                                },
                            });
                        }
                        that.serverTime = Object.keys(obj).reverse();
                        that.draw();
                    }
                });
            },
            createDNS () {
                if (!this.validNewServer()) return;
                var that = this;
                // 创建新服务器
                indexAjax.post({
                    url : 'http://hfdns-test.ipo.com/dns/servers',
                    data : that.newServer,
                    success : function (response) {
                        Alert('创建成功');
                        that.select1();
                        taht.getServer();
                    }
                });
                this.$refs.addDialog.hide();
            },
            draw () {
                var that = this;
                setTimeout(function () {
                    document.querySelector('#echarts1').style.height = '400px';
                    echarts.init(document.querySelector('#echarts1')).setOption({
                        color: ['#7CBDE8', '#F0786A'],
                        title : false,
                        grid : {
                            x : 70,
                            y : 70,
                            x2 : 50
                        },
                        tooltip : {
                            trigger: 'axis',
                        },
                        legend: {
                            data: that.serverName,
                            x: 50
                        },
                        xAxis : [
                            {
                                type : 'category',
                                boundaryGap : false,
                                data : that.serverTime,
                            },
                            
                        ],
                        yAxis : [
                            {
                                type : 'value',
                                axisLabel : {
                                    formatter: '{value}'
                                },
                                axisLabel : {
                                    formatter: that.formatter
                                }
                            }
                        ],
                        series : that.series
                    }, true);
                });
            },
            // 2017-08-20 11:09:25
            getTime : function (stamp) {
                var time = this.date(stamp);
                return time[0] + '-' + time[1] + '-' + time[2] + ' ' + time[3] + ':' + time[4] + ':' +  time[5];
            },
            // 返回当前日期信息
            date : function(time) {
                var n = new Date(time);
                return [n.getFullYear(), this.fillZero(n.getMonth() + 1), this.fillZero(n.getDate()), this.fillZero(n.getHours()), this.fillZero(n.getMinutes()), this.fillZero(n.getSeconds())];
            },
            // 这个没有脱离形
            fillZero : function (nub) {
                return nub < 10 ? '0' + nub : nub;
            },
            formatter : function (data){
                return data/10000 + 'w';
            }
        }
    }
    

        
    
</script>
<style scoped lang="less">
@media (min-width: 992px) {
    .col-md-3{
        width:100%;
        
    }
    .col-md-3 .server-status-block{
        width:100%;
    }
}
.col-md-3 .server-status-block{
    width:30%;
    margin:1%;
    background-color:#fff;
}
/* 服务器状态 */
.snow.add{
    box-shadow:-7px 0 0 0 #72BFF0;
    div{
        font-size:16px;
        width:66px;
        line-height:26px;
        border-radius:20px;
        text-align:center;
        font-size:12px;
        color:#72BFF0;
        position:absolute;
        top:0;
        height:26px;
        bottom:0;
        right:10px;
        margin:auto;
        background-color:#C8EAFF;
        border:1px solid #72BFF0;
        cursor:pointer;
    }
    h4{
        text-indent:20px;
        margin-top:20px;
    }
}
.snow{
    position:relative;
    width:30%;
    margin:1%;
    float:left;
    border:1px solid #e8e8e8;
    border-left:none;
    background-color:#fff;
    box-shadow:-7px 0 0 0 #66DAB7;
    font-size:12px;
    height:72px;
    .serverHost{
        font-size:16px;
    }
    h4:nth-of-type(2){
        text-indent:20px;
        margin-bottom:20px;
    }
    ul{
        margin-left:20px;
        li{
            margin:0 5px;
        }
    }
    .serverStatusName{
        font-size:16px;
        width:66px;
        line-height:26px;
        border-radius:20px;
        text-align:center;
        font-size:12px;
        
        position:absolute;
        top:0;
        height:26px;
        bottom:0;
        right:10px;
        margin:auto;
    }
    li{
        display:inline-block;
        span{
            color:#8096AB;
        }
        

    }
    li span:nth-of-type(1){
        display:inline-block;
        width: 11px;
        height: 11px;
        background-color: #6BE7C2;
        background-size: contain;
        border: 3px solid #D8FFF4;
        box-shadow:0 0 0 2px #6BE7C2;
        border-radius: 100%;
        margin-right:7px;
    }
}

.snow.yes{
    .serverStatusName{
        border:1px solid #75DFBF;
        background-color:#D7FFF3;
        color:#56CCA9;

    }
}
.snow.no{
    box-shadow:-7px 0 0 0 #EF786A;
    .serverStatusName{
        border:1px solid #EF786A;
        background-color:#FFD4CF;
        color:#EF786A;

    }
    .red{
        background-color:#EF786A;
        box-shadow:0 0 0 2px #EF786A;
        border:3px solid #FFD4CF;
    }
}

    .top{
        border: 1px #ccc solid;
        height: 100px;
    }
    .top-counter-wrap{
        display: flex;
    }
    .content-wrap{
        display: flex;
        flex-wrap: wrap;
    }

    .column-0 .water-fall-item{
        margin-right: 10px;
    }
    .column-1 .water-fall-item{
        margin-left: 10px;
    }
</style>
<style>
    .top-counter-wrap .record-count{
        margin-right: 0;
    }
</style>