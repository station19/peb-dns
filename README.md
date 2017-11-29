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


#### 4，环境搭建

* 本教程基于Ubuntu/Debian，已安装python3 环境的请跳过

* 克隆项目代码到本地
```bash
# 将本仓库clone到本地
git clone xxx@xxx:haofang/peb-dns.git
```

* 工具安装
```bash
# 安装python3环境
# 本项目基于Python3.5，如已安装，请略过。
sudo apt-get update
sudo apt-get install python3-pip python3-dev
sudo apt-get install build-essential libssl-dev libffi-dev python-dev

# 安装 mysql 略  (请安装mysql5.7版本)
sudo apt-get install mysql-server
# 安装 etcd 略  （请参考官方文档）
sudo apt-get install etcd

```


* 安装依赖

首先进入当前目录下
```bash
pip3 install -r requirements.txt

# 下载页面 https://dev.mysql.com/downloads/connector/python/
# 选择 Platform Independent, 下载mysql驱动 mysql-connector-python==2.1.7
# 解压后，进入文件夹然后运行

python setup.py install

```


* 初始化数据库

1，创建数据库
```bash
# 进入当前项目根目录下
❯ mysql -u root -p

mysql> create database <your_db_name>;
Query OK, 1 row affected (0.01 sec)

mysql> ^DBye
```

2，当前目录下修改配置文件 
prod.cfg （生产环境配置文件）
里面所有字段都有详细说明，请严格按照按照说明一一配好。


3，初始化数据库
```bash
source env.sh
flask db init
flask db migrate
flask db upgrade
flask db initdb
```


#### 简单快速部署方式

进入当前项目根目录下，运行以下命令部署
```bash
nohup gunicorn -w 4 hf_dns:app -b 0.0.0.0:8080 --log-level=debug &
```
PS: 上面 -w 为 开启workers数，公式：（系统内核数*2 + 1)



