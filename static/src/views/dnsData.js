// logs页
let logs = {
    // 搜索
    searchLogData : {
        id : {
            name : 'id',
            value : '',
            type : 'text',
        },
        operator : {
            name : '操作者',
            value : '',
            type : 'text',
        },
        operation_type : {
            name : '操作类型',
            value : '',
            display : ['全部', '添加', '修改', '删除'],
            type : 'select',
        },
        target_type : {
            name : '资源类型',
            value : '',
            display : ['全部', 'SERVER', 'VIEW', 'ZONE', 'RECORD', 'USER', 'ROLE', 'PRIVILEGE', 'PAGE'],
            type : 'select',
        },
        target_name : {
            name : '资源名称',
            value : '',
            type : 'text',
        },
        target_id : {
            name : '资源ID',
            value : '',
            type : 'text',
        },
    },
    // 表格
    table_base: {
        col: {
            target_detail: {
                label: '对象详情',
                width: '500px',
            },
            target_type : '对象类型',
            operation_type: '操作类型',
            target_name: '对象名称',
            target_id: '操作对象',
            operator : '操作者',
            id : '对象ID',
            operation_time : '操作时间',
        },
    },
    // 分页
    pager: {
        current: 1,
        total: 10,
        volumn: 10
    },
}



// 域名页
let domainmanager = {
    recordEmpty : {
        host:"",
        id:"",
        record_type:"",
        ttl:'',
        value:"",
        view_name:"",
    },
    searchRecordDataEmpty : {
        id : {
            name : 'id',
            value : '',
            type : 'text',
        },
        host : {
            name : '记录主机',
            value : '',
            type : 'text',
        },
        record_type : {
            name : '记录类型',
            value : '',
            display : [{label:'全部', value: ''},'A', 'CNAME', 'PTR', 'NS'],
            type : 'select',
        },
        ttl : {
            name : 'ttl',
            value : '',
            display : [{label:'全部', value: ''},600, 1800, 3600],
            type : 'select',
        },
        value : {
            name : '记录值',
            value : '',
            type : 'text',
        },
        view_name : {
            name : '线路类型',
            value : '',
            display : [],
            type : 'select',
        }
    },
    gridColumn : {
        id: 'ID',
        host: '主机记录',
        record_type: '记录类型',
        value: '记录值',
        ttl: 'TTL',
        view_name: '线路类型',
        comment: '备注',
        option: {
            type: 'action',
            label: '操作',
            width: '150px;',
        }
    },
    pager : {
        current: 5,
        total: 150,
        volumn: 20
    },
};



// dns服务器页
let dnsServer = {
    newServerEmpty : {
        host : '', 
        ip : '',
        env : '',
        dns_server_type : '',
        zb_process_itemid : '',
        zb_port_itemid : '',
        zb_resolve_itemid : '',
        zb_resolve_rate_itemid : '',
    },
    searchServerDataEmpty : {
        id : {
            name : 'id',
            value : '',
            type : 'text',
        },
        host : {
            name : '用户名',
            value : '',
            type : 'text',
        },
        ip : {
            name : 'IP地址',
            value : '',
            type : 'text',
        },
        env : {
            name : '环境',
            value : '',
            display : [{label:'全部', value: ''},'dev', 'anhouse', 'ga'],
            type : 'select',
        },
        dns_server_type : {
            name : '服务器类型',
            value : '',
            display : [{label:'全部', value: ''},'master', 'salve'],
            type : 'select',
        },
    },
    gridColumn : {
        id: {
            label: 'ID',
            width: '80px'
        },
        host: 'Host',
        ip: ' IP地址    ',
        env: ' 环境',
        dns_server_type: ' DNS类型',
        option: {
            type: 'action',
            label: '操作',
            width: '130px'
        }
    },
    pager : {
        current: 1,
        total: 0,
        volumn: 10
    }
};



// view页
var view = {
    emptyView : {
        name:'',
        acl:''
    },
    searchViewDataEmpty : {
        id : {
            name : 'id',
            value : '',
            type : 'text',
        },
        name : {
            name : '名称',
            value : '',
            type : 'text',
        }
    },
    pager : {
        current: 1,
        total: 0,
        volumn: 6
    },
    gridColumn : {
        id: {
            label: 'ID',
            width: '50px'
        },
        name: ' View名称',
        acl: '区域配置（ACL）',
        option: {
            type: 'action',
            label: '操作',
            width: '120px'
        }
    },
};



// 全部的数据
let allData = {
    logs,
    domainmanager,
    dnsServer,
    view,
};

export default (str) => {
    return allData[str];
};