# 环境搭建

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

2，修改配置文件 
首先进入当前项目根目录， 然后进入 config 子目录，配置文件路径如下：
peb-dns/config/prod.cfg
里面所有字段都有详细说明，请严格按照按照说明一一配好。


3，配置应用环境变量
```bash
#设置 FLASK_APP 环境变量，值为本项目根目录下 app.py 的绝对路径
#首先进入当前项目根目录下，即 app.py 同级目录，然后执行以下语句
export FLASK_APP=${PWD}/app.py
```

4，初始化数据库
```bash
flask db init
flask db migrate
flask db upgrade
flask initdb
```



#### 简单快速部署方式

进入当前项目根目录下，运行以下命令部署
```bash
nohup gunicorn -w 4 app:app -b 0.0.0.0:8080 --log-level=debug &
```
PS: 上面 -w 为 开启workers数，公式：（系统内核数*2 + 1)
    8080 为端口号



