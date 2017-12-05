PEB-DNS 管理平台
===========================
该项目用于公司内部多 IDC 的 dns 管理。
****
### Author: 平安好房运维团队出品
### E-mail: ml_12383@pingan.com.cn
### QQ群: 378248675
### 有任何问题，可以通过邮件形式交流。

****

# 平台架构图如下：

![dns](/docs/images/dns.jpg "DNS平台架构图")

功能介绍
------

#### 1， DNS 管理方式：

公司使用 BIND 搭建 DNS 服务器。

平台使用 ETCD 来管理 DNS 服务器的 BIND 配置文件，包括 VIEW，ZONE，RECORD 的各个配置文件。

所有的 DNS 服务器的配置文件和数据都是统一从 ETCD 上获取，因此所有 DNS 服务器的配置文件及数据都是相同的，且所有 DNS 服务器类型均为 master，不存在 slave。

所有DNS服务器会实时监测 ETCD 上的数据，当在平台上对 DNS 进行操作时，只要配置文件发生变化，所有DNS服务器都会实时获取到最新的配置文件信息。

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

