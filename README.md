平安好房DNS管理平台
===========================
该项目用于 `平安好房` 系统运维组管控公司DNS 
****
### Author: 平安好房运维团队出品
### E-mail: xxx.pingan.com.cn
****

# 平台架构图如下：

![dns](/dns.jpg "DNS平台架构图")

功能介绍
------

#### 1， DNS管理方式：

公司使用 BIND 搭建DNS服务器。

平台使用ETCD来管理DNS服务器的BIND配置文件，包括VIEW，ZONE，RECORD的各个配置文件。

所有的DNS服务器的配置文件和数据都是统一从ETCD获取，因此所有DNS服务器的配置文件及数据都是相同的，且所有DNS服务器类型均为master，不存在slave。

当再平台上对DNS进行操作时，只要配置文件有变化，所有服务器均能从ETCD上获取最新的配置文件。

#### 2，使用技术栈：

后端： Python3.5 + Flask + Mysql + Etcd

前端： Vue.js

架构： 前后端分离，纯restful架构，后端只提供restful api，前端用vue框架。


#### 3，功能简介

* DNS服务器管理

* BIND主配置文件管理

* View管理 (区域)

* Zone管理 （域名）

* Record管理 （子域名）

    * 内网域名Record管理

    * 劫持域名Record管理

    * 公网域名Record管理

* 平台权限管理
    * 用户管理
    * 角色管理 
    * 权限管理 

* 操作记录


#### 4，搭建

* 可查看[环境搭建文档](docs/deploy.md)