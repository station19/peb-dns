平安好房DNS管理平台API文档
===========================

# 认证
### 1，LDAP认证接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/auth/login_ldap       |post 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
username    |string     |是       |无     |user123      |用户名
password    |string     |是       |无     |passwd123      |密码

#### 返回格式：
#### 返回格式：


```json
认证成功
状态码： 200
{
    "token": "eyJ0eXasdfasdfasdfasdfasdfJ9.eyJ1c2VyIjoiTElKSUFKSUE4NzMiLCJleHAiOjE1MTIwNTA0MTh9.vJ_kj2SSf3T_0TyO5_Y4NN4l7aqXwyr0n01kKRdZW6s",
    "user_info": {
        "id": 3,
        "username": "user123",
        "email": "xx",
        "chinese_name": "",
        "cellphone": "xx",
        "position": "xx",
        "location": "",
        "can_add_server": true,
        "can_add_view": true,
        "can_add_zone": true,
        "member_since": "2017-11-23 18:24:22"
    }
}


认证失败
状态码：403
{
    "message": "认证失败！"
}
```

### 2，本地用户认证接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/auth/login_ldap       |post 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
username    |string     |是       |无     |user123      |用户名
password    |string     |是       |无     |passwd123      |密码

#### 返回格式：


```json
认证成功
状态码： 200
{
    "token": "eyJ0eXasdfasdfasdfasdfasdfJ9.eyJ1c2VyIjoiTElKSUFKSUE4NzMiLCJleHAiOjE1MTIwNTA0MTh9.vJ_kj2SSf3T_0TyO5_Y4NN4l7aqXwyr0n01kKRdZW6s",
    "user_info": {
        "id": 3,
        "username": "user123",
        "email": "xx",
        "chinese_name": "",
        "cellphone": "xx",
        "position": "xx",
        "location": "",
        "can_add_server": true,
        "can_add_view": true,
        "can_add_zone": true,
        "member_since": "2017-11-23 18:24:22"
    }
}

认证失败
状态码：403
{
    "message": "认证失败！"
}
```

### 3，本地新用户注册接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/auth/register_local       |post 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
username    |string     |是       |无     |user123      |用户名
password    |string     |是       |无     |passwd123      |密码
password2    |string     |是       |无     |passwd123      |密码
email    |string     |是       |无     |xxx@qq.com      |邮箱

#### 返回格式：


```json
认证成功
状态码： 200
{
    "message": "OK"
}

认证失败
状态码：400
{
    "message": "Failed",
    "error": "用户已存在！"
}
```

# DNS相关资源
## 一，DNS服务器（Server）
### 1.1，DNS服务器列表获取接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/servers        |get 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
currentPage    |int     |否       |1     |3      |当前是第几页
pageSize    |int     |否       |10     |20      |每页显示的记录数
id    |int     |否       |无     |20      |ID
host    |string     |否       |无     |www      |用户名
ip    |string     |否       |无     |10.2.2.2      |IP地址
env    |string     |否       |无     |env      |环境
dns_server_type    |string     |否       |无     |master      |服务器类型


#### 返回格式：


```json
获取成功
状态码： 200
{
    "total": 4,
    "servers": [
        {
            "id": 6,
            "host": "ooo",
            "ip": "0.0.0.5",
            "env": "anhouse",
            "dns_server_type": "salve",
            "zb_process_itemid": "123",
            "zb_port_itemid": "123",
            "zb_resolve_itemid": "123",
            "zb_resolve_rate_itemid": "123",
            "can_update": true,
            "can_delete": true
        },
        {
            "id": 5,
            "host": "ss3",
            "ip": "0.0.0.4.0",
            "env": "dev",
            "dns_server_type": "salve",
            "zb_process_itemid": "123",
            "zb_port_itemid": "123",
            "zb_resolve_itemid": "123",
            "zb_resolve_rate_itemid": "320857",
            "can_update": true,
            "can_delete": true
        },
        {
            "id": 2,
            "host": "s2",
            "ip": "0.0.0.1",
            "env": "anhouse",
            "dns_server_type": "master",
            "zb_process_itemid": "222",
            "zb_port_itemid": "222",
            "zb_resolve_itemid": "222",
            "zb_resolve_rate_itemid": "189254",
            "can_update": true,
            "can_delete": true
        },
        {
            "id": 1,
            "host": "s1",
            "ip": "0.0.0.0",
            "env": "dev",
            "dns_server_type": "master",
            "zb_process_itemid": "111",
            "zb_port_itemid": "111",
            "zb_resolve_itemid": "111",
            "zb_resolve_rate_itemid": "189243",
            "can_update": true,
            "can_delete": true
        }
    ],
    "current_page": 1
}

```

### 1.2，DNS服务器创建接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/servers        |post 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
host    |string     |是       |无     |www      |用户名
ip    |string     |是       |无     |10.2.2.2      |IP地址
env    |string     |是       |无     |env      |环境
dns_server_type    |string     |否       |无     |master      |服务器类型
zb_process_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS解析进程的itemid
zb_port_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS服务器端口的itemid
zb_resolve_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS解析的itemid
zb_resolve_rate_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS解析量的itemid


#### 返回格式：


```json
创建成功
状态码： 200
{
    "message":"OK"
} 
创建失败
状态码： 400
{
    "message":"Failed",
    "error": "xxxx"
} 
```

### 1.3，获取指定ID的DNS服务器信息接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/servers/\<int:server_id>        |get 


#### 参数列表：
无


#### 返回格式：

```json
获取成功
状态码： 200
{
    "id": 1,
    "host": "s1",
    "ip": "0.0.0.0",
    "env": "dev",
    "dns_server_type": "master",
    "zb_process_itemid": "111",
    "zb_port_itemid": "111",
    "zb_resolve_itemid": "111",
    "zb_resolve_rate_itemid": "189243",
    "can_update": true,
    "can_delete": true
}
```

### 1.4，修改指定ID的DNS服务器接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/servers/\<int:server_id>        |put 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
host    |string     |是       |无     |www      |用户名
ip    |string     |是       |无     |10.2.2.2      |IP地址
env    |string     |是       |无     |env      |环境
dns_server_type    |string     |否       |无     |master      |服务器类型
zb_process_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS解析进程的itemid
zb_port_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS服务器端口的itemid
zb_resolve_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS解析的itemid
zb_resolve_rate_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS解析量的itemid

#### 返回格式：


```json
修改成功
状态码： 200
{
    "message":"OK"
} 
修改失败
状态码： 400
{
    "message":"Failed",
    "error": "xxxx"
} 
```

### 1.5，删除指定ID的DNS服务器接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/servers/\<int:server_id>        |delete 


#### 参数列表：
无


#### 返回格式：


```json
删除成功
状态码： 200
{
    "message":"OK"
} 
删除失败
状态码： 400
{
    "message":"Failed",
    "error": "xxxx"
} 
```


## 二，DNS区域（View）
### 2.1，DNS区域列表获取接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/views        |get 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
currentPage    |int     |否       |1     |3      |当前是第几页
pageSize    |int     |否       |10     |20      |每页显示的记录数
id    |int     |否       |无     |20      |ID
name    |string     |否       |无     |view1      |View名称

#### 返回格式：


```json
获取成功
状态码： 200
{
    "total": 3,
    "views": [
        {
            "id": 5,
            "name": "jtest",
            "acl": "10.21.21.25\n0.0.0.0",
            "can_update": true,
            "can_delete": true
        },
        {
            "id": 2,
            "name": "vvvv111111111",
            "acl": "0.0.0.0",
            "can_update": true,
            "can_delete": true
        },
        {
            "id": 1,
            "name": "wqerqwer",
            "acl": "0.0.0.0\n1.1.1.1",
            "can_update": true,
            "can_delete": true
        }
    ],
    "current_page": 1
}

```


### 2.2，DNS区域创建接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/views        |post 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
name    |string     |是       |无     |v6      |view名称
acl    |string     |是       |无     |0.0.0.0\n1.1.1.1      |acl IP地址列表


#### 返回格式：


```json
创建成功
状态码： 200
{
    "message":"OK"
} 
创建失败
状态码： 400
{
    "message":"Failed",
    "error": "xxxx"
} 
```

### 2.3，获取指定ID的DNS区域信息接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/views/\<int:view_id>        |get 


#### 参数列表：
无


#### 返回格式：


```json
{
    "id": 1,
    "name": "wqerqwer",
    "acl": "0.0.0.0\n1.1.1.1",
    "can_update": true,
    "can_delete": true
}
```


### 2.4，修改指定ID的DNS区域接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/views/\<int:view_id>        |put 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
name    |string     |是       |无     |v6      |view名称
acl    |string     |是       |无     |0.0.0.0\n1.1.1.1      |acl IP地址列表


#### 返回格式：


```json
修改成功
状态码： 200
{
    "message":"OK"
} 
修改失败
状态码： 400
{
    "message":"Failed",
    "error": "xxxx"
} 
```


### 2.5，删除指定ID的DNS区域接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/views/\<int:view_id>        |delete 


#### 参数列表：
无


#### 返回格式：


```json
删除成功
状态码： 200
{
    "message":"OK"
} 
删除失败
状态码： 400
{
    "message":"Failed",
    "error": "xxxx"
} 
```





## 三，DNS域名（Zone）
### 3.1，DNS域名列表获取接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/zones        |get 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
currentPage    |int     |否       |1     |3      |当前是第几页
pageSize    |int     |否       |10     |20      |每页显示的记录数
id    |int     |否       |无     |20      |ID
name    |string     |否       |无     |z1      |Zone名称
zone_group    |string     |否       |无     |2      |Zone归属， 内部（1）/外部（0）/劫持（2）
zone_type    |string     |否       |无     |master      |Zone类型， master/forward only
	

#### 返回格式：


```json
获取成功
状态码： 200

{
    "total": 6,
    "zones": [
        {
            "id": 6,
            "name": "xxx123.com",
            "zone_group": 1,
            "zone_type": "forward only",
            "forwarders": "0.0.0.0; 1.1.1.1;",
            "view_name_list": "['wqerqwer', 'vvvv111111111', 'jtest']",
            "can_update": true,
            "can_delete": true,
            "view_ids": [
                1,
                2,
                5
            ]
        },
        {
            "id": 5,
            "name": "xx2.com",
            "zone_group": 2,
            "zone_type": "master",
            "forwarders": "",
            "view_name_list": "['wqerqwer', 'vvvv111111111', 'jtest']",
            "can_update": true,
            "can_delete": true,
            "view_ids": [
                1,
                2,
                5
            ]
        },
        {
            "id": 4,
            "name": "xx1.com",
            "zone_group": 1,
            "zone_type": "master",
            "forwarders": "",
            "view_name_list": "['wqerqwer', 'vvvv111111111', 'jtest']",
            "can_update": true,
            "can_delete": true,
            "view_ids": [
                1,
                2,
                5
            ]
        }
    ],
    "current_page": 1
}
```


### 3.2，DNS域名创建接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/zones        |post 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
name    |string     |是       |无     |v6      |zone名称
zone_group    |string     |否       |无     |2      |Zone归属， 内部（1）/外部（0）/劫持（2）
zone_type    |string     |是      |无     |master      |Zone类型， master/forward only
forwarders    |string     |否       |无     |0.0.0.0\n1.1.1.1      |转发至的地址
view_ids    |list     |是       |无     |[1,2,3]      |关联一个或多个view到当前zone

#### 返回格式：


```json
创建成功
状态码： 200
{
    "message":"OK"
} 
创建失败
状态码： 400
{
    "message":"Failed",
    "error": "xxxx"
} 
```

### 3.3，获取指定ID的DNS域名信息接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/zones/\<int:zone_id>        |get 


#### 参数列表：
无


#### 返回格式：


```json
获取成功
状态码： 200
{
    "id": 2,
    "name": "fw3efwwv.com",
    "zone_group": 1,
    "zone_type": "master",
    "forwarders": "",
    "view_name_list": "['wqerqwer', 'vvvv111111111', 'jtest']",
    "can_update": true,
    "can_delete": true,
    "view_ids": [1, 2, 5]
}
```


### 3.4，修改指定ID的DNS域名接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/zones/\<int: zone_id>        |put 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
name    |string     |是       |无     |v6      |zone名称
zone_group    |string     |否       |无     |2      |Zone归属， 内部（1）/外部（0）/劫持（2）
zone_type    |string     |是      |无     |master      |Zone类型， master/forward only
forwarders    |string     |否       |无     |0.0.0.0\n1.1.1.1      |转发至的地址
view_ids    |list     |是       |无     |[1,2,3]      |关联一个或多个view到当前zone


#### 返回格式：


```json
修改成功
状态码： 200
{
    "message":"OK"
} 
修改失败
状态码： 400
{
    "message":"Failed",
    "error": "xxxx"
} 
```


### 3.5，删除指定ID的DNS域名接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/zones/\<int:zone_id>        |delete 


#### 参数列表：
无


#### 返回格式：


```json
删除成功
状态码： 200
{
    "message":"OK"
} 
删除失败
状态码： 400
{
    "message":"Failed",
    "error": "xxxx"
} 
```



## 四，DNS域名记录（Record）
### 4.1，DNS域名记录列表获取接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/records        |get 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
zone_id    |int     |是       |无     |20      |所属的Zone的ID
currentPage    |int     |否       |1     |3      |当前是第几页
pageSize    |int     |否       |10     |20      |每页显示的记录数
id    |int     |否       |无     |20      |ID
host    |string     |否       |无     |www      |用户名
record_type    |string     |否       |无     |A      |记录类型
ttl    |string     |否       |无     |600      |TTL
value    |string     |否       |无     |127.0.0.1      |记录值
view_name    |string     |否       |无     |v1      |线路

#### 返回格式：


```json
获取成功
状态码： 200
{
    "total": 9,
    "records": [
        {
            "id": 26,
            "host": "123123",
            "record_type": "CNAME",
            "ttl": "1800",
            "value": "0.0.0.0",
            "view_name": "vvvv111111111",
            "comment": "123",
            "zone_id": 2,
            "can_update": true,
            "can_delete": true
        },
        {
            "id": 25,
            "host": "23123123",
            "record_type": "A",
            "ttl": "600",
            "value": "0.0.0.0",
            "view_name": "jtest",
            "comment": "123123",
            "zone_id": 2,
            "can_update": true,
            "can_delete": true
        },
        {
            "id": 24,
            "host": "23123123",
            "record_type": "A",
            "ttl": "600",
            "value": "0.0.0.0",
            "view_name": "vvvv111111111",
            "comment": "123123",
            "zone_id": 2,
            "can_update": true,
            "can_delete": true
        }
    ],
    "current_page": 1
}

```

### 4.2，DNS域名记录创建接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/records        |post 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
host    |string     |是       |无     |r1      |record名称
record_type    |string     |否       |无     |2      |Zone归属， A/NS/PTR/CNAME
ttl    |string     |是      |无     |600      |TTL值
value    |string     |是       |无     |1.1.1.1      |记录值，必须为ip地址
view_name    |string     |是       |无     |v1      |关联的view名称
comment    |string     |是       |无     |comment      |备注
zone_id    |int     |是       |无     |2     |当前record所属zone的ID

#### 返回格式：


```json
创建成功
状态码： 200
{
    "message":"OK"
} 
创建失败
状态码： 400
{
    "message":"Failed",
    "error": "xxxx"
} 
```

### 4.3，获取指定ID的DNS域名记录信息接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/records/\<int:record_id>        |get 


#### 参数列表：
无


#### 返回格式：


```json
获取成功
状态码： 200
{
    "id": 6,
    "host": "xxx111",
    "record_type": "A",
    "ttl": "600",
    "value": "0.0.0.0",
    "view_name": "vvvv111111111",
    "comment": "xxx111",
    "zone_id": 2,
    "can_update": true,
    "can_delete": true
}
```


### 4.4，修改指定ID的DNS域名记录接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/records/\<int:record_id>        |put 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
host    |string     |是       |无     |r1      |record名称
record_type    |string     |否       |无     |2      |Zone归属， A/NS/PTR/CNAME
ttl    |string     |是      |无     |600      |TTL值
value    |string     |是       |无     |1.1.1.1      |记录值，必须为ip地址
view_name    |string     |是       |无     |v1      |关联的view名称
comment    |string     |是       |无     |comment      |备注
zone_id    |int     |是       |无     |2     |当前record所属zone的ID


#### 返回格式：


```json
修改成功
状态码： 200
{
    "message":"OK"
} 
修改失败
状态码： 400
{
    "message":"Failed",
    "error": "xxxx"
} 
```


### 4.5，删除指定ID的DNS域名记录接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/records/\<int:record_id>        |delete 


#### 参数列表：
无


#### 返回格式：


```json
删除成功
状态码： 200
{
    "message":"OK"
} 
删除失败
状态码： 400
{
    "message":"Failed",
    "error": "xxxx"
} 
```