import logging
import time
import subprocess
import os
import signal
import sys
import etcd
from flask import current_app
import requests
import json
import copy
from datetime import datetime
from collections import OrderedDict
# current_app._get_current_object()

# from peb_dns.models.dns import DBDNSServer
# from peb_dns.common.decorators import token_required
# from peb_dns import db



ZONE_GROUP_MAPPING = {
    0:"外部域名",
    1:"内部域名",
    2:"劫持域名"
}

#获取ETCD客户端
def getETCDclient():
    client = etcd.Client(host=current_app.config.get('ETCD_SERVER_HOST'), port=current_app.config.get('ETCD_SERVER_PORT'))
    try:
        client.read(current_app.config.get('BIND_CONF'))
    except etcd.EtcdKeyNotFound:
        client.write(current_app.config.get('BIND_CONF'), '', prevExist=False)

    try:
        client.read(current_app.config.get('VIEW_DEFINE_CONF'))
    except etcd.EtcdKeyNotFound:
        client.write(current_app.config.get('VIEW_DEFINE_CONF'), '', prevExist=False)
    return client


def getLogger(log_path):
    # logger初始化
    logger = logging.getLogger('DNS')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_path)
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


class ResourceContent(object):

    @staticmethod
    def getViewContent(view, prefix=None):
        content = 'id: ' + str(view.id) + '\n' \
        + 'View名称: ' + str(view.name) + '\n' \
        + 'ACL: ' + str(view.acl) + '\n'

        if prefix:
            content = prefix + '\n' + content
        return content

    @staticmethod
    def getZoneContent(zone, prefix=None):
        content = 'id: ' + str(zone.id) + '\n' \
        + 'Zone名称: ' + str(zone.name) + '\n' \
        + 'Zone归属: ' + ZONE_GROUP_MAPPING.get(zone.zone_group) + '\n' \
        + 'Zone类型: ' + str(zone.zone_type) + '\n' \
        + '关联View: ' + str(zone.view_name_list) + '\n' 

        if prefix:
            content = prefix + '\n' + content
        return content

    @staticmethod
    def getRecordContent(record, prefix=None):
        #'修改前内容：'
        content = 'id: ' + str(record.id) + '\n' \
        + '记录主机: ' + str(record.host) + '\n' \
        + '记录类型: ' + str(record.record_type) + '\n' \
        + '记录值: ' + str(record.value) + '\n' \
        + 'TTL: ' + str(record.ttl) + '\n' \
        + '线路类型: ' + str(record.view_name) + '\n' \
        + '备注: ' + str(record.comment) + '\n' \
        + '创建人: ' + str(record.creator) + '\n' \
        + '创建时间: ' + str(record.gmt_create)

        if prefix:
            content = prefix + '\n' + content
        return content

    @staticmethod
    def getServerContent(server, prefix=None):
        #'修改前内容：'
        content = 'id: ' + str(server.id) + '\n' \
        + '主机名: ' + str(server.host) + '\n' \
        + 'IP地址: ' + str(server.ip) + '\n' \
        + '环境: ' + str(server.env) + '\n' \
        + 'DNS类型: ' + str(server.dns_server_type) + '\n'

        if prefix:
            content = prefix + '\n' + content
        return content


def killProcesses(ppid=None):
    ppid = str(ppid)
    pidgrp = []
    def GetChildPids(ppid):
        command = "ps -ef | awk '{if ($3 ==%s) print $2;}'" % str(ppid)
        pids = os.popen(command).read()
        pids = pids.split()
        return pids
    pidgrp.extend(GetChildPids(ppid))
    for pid in pidgrp:
        pidgrp.extend(GetChildPids(pid))

    pidgrp.insert(0, ppid)
    while len(pidgrp) > 0:
        pid = pidgrp.pop()
        try:
            os.kill(int(pid), signal.SIGKILL)
            return True
        except OSError:
            try:
                os.popen("kill -9 %d" % int(pid))
                return True
            except Exception:
                return False



DEFAULT_CMD_TIMEOUT = 1200
def doCMDWithOutput(cmd, time_out = None):
    if time_out is None:
        time_out = DEFAULT_CMD_TIMEOUT
    # LOG.info("Doing CMD: [ %s ]" % cmd)
    pre_time = time.time()
    output = []
    cmd_return_code = 1
    cmd_proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    while True:
        output_line = cmd_proc.stdout.readline().decode().strip("\r\n")
        cmd_return_code = cmd_proc.poll()
        elapsed_time = time.time() - pre_time
        if cmd_return_code is None:
            if elapsed_time >= time_out:
                killProcesses(ppid=cmd_proc.pid)
                # LOG.error("Timeout to exe CMD")
                return False
        elif output_line == '' and cmd_return_code is not None:
            break

        # sys.stdout.write("%s\n" % output_line)
        sys.stdout.flush()
        if output_line.strip() != '':
            output.append(output_line)
    return (cmd_return_code, output)



# def initServer(cmd, app_object, server_id):
#     with app_object.app_context():
#         # print(server_id)
#         current_server = DBDNSServer.query.get(int(server_id))
#         res = doCMDWithOutput(cmd)
#         if not res:
#             current_server.status = '初始化失败'
#             current_server.logs = '超时！！初始化时间已超过20分钟'
#             db.session.add(current_server)
#             db.session.commit()
#             return False, ['超时！！初始化时间已超过20分钟！']
#         cmd_return_code, output = res
#         if cmd_return_code != 0:
#             print('\n'.join(output))
#             current_server.status = '初始化失败'
#             current_server.logs = '\n'.join(output)
#             db.session.add(current_server)
#             db.session.commit()
#             return False, output
#         else:
#             print('\n'.join(output))
#             current_server.status = 'ONLINE'
#             current_server.logs = '\n'.join(output)
#             db.session.add(current_server)
#             db.session.commit()
#             return True, output


class DNSRecord(object):

    def __init__(self, group, data, script):
        self.__group = group
        self.__data = data
        self.__script = script
        self.__create_url = current_app.config.get('DNSPOD_RECORD_BASE_URL') + 'Create'
        self.__modify_url = current_app.config.get('DNSPOD_RECORD_BASE_URL') + 'Modify'
        self.__delete_url = current_app.config.get('DNSPOD_RECORD_BASE_URL') + 'Remove'
        self.__body_info = {"login_token":current_app.config.get('DNSPOD_TOKEN'), "format": current_app.config.get('DNSPOD_DATA_FORMAT')}

    def create(self):
        if self.__group == 'outter':
            return self.__outter_execute(self.__create_url, self.__data)
        return doCMDWithOutput(self.__script)

    def modify(self):
        if self.__group == 'outter':
            return self.__outter_execute(self.__modify_url, self.__data)
        return doCMDWithOutput(self.__script)

    def delete(self):
        if self.__group == 'outter':
            return self.__outter_execute(self.__delete_url, self.__data)
        return doCMDWithOutput(self.__script)

    def __outter_execute(self, url, data):
        try:
            res = requests.post(url, data=dict(self.__body_info, **data))
            if res.status_code == 200:
                res_json = res.json()
                if res_json.get('status').get('code') == '1':
                    return 0, res_json
                return 1, [str(res_json)]
            return 1, [str(res_json)]
        except Exception as e:
            return 1, [e.__str__]

    def failHandler(self):
        pass

    def isDomainExists(self):
        pass



class DNSPod(object):

    @staticmethod
    def getDNSPodLines(domain):
        body_info = {"login_token": current_app.config.get('DNSPOD_TOKEN'), "format": current_app.config.get('DNSPOD_DATA_FORMAT'), "domain": domain}
        try:
            res = requests.post(current_app.config.get('DNSPOD_LINE_URL'), data=body_info)
        except Exception as e:
            return []
        if res.status_code >= 200 and res.status_code <= 220:
            return res.json()['lines']
        return []

    @staticmethod
    def getDNSPodTypes(domain):
        body_info = {"login_token": current_app.config.get('DNSPOD_TOKEN'), "format": current_app.config.get('DNSPOD_DATA_FORMAT'), "domain": domain}
        try:
            res = requests.post(current_app.config.get('DNSPOD_TYPE_URL'), data=body_info)
        except Exception as e:
            return []
        if res.status_code >= 200 and res.status_code <= 220:
            return res.json()['lines']
        return []




class ZBapi(object):
    def __init__(self, server):
        self._url = current_app.config.get('ZABBIX_URL')
        self._header = {"Content-Type":"application/json"}
        self._server = server

    def _get_authid(self):
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": current_app.config.get('ZABBIX_USERNAME'),
                "password": current_app.config.get('ZABBIX_PASSWORD')
            },
            "id": 1,
            "auth":None
        }

        try:
            r = requests.post(self._url, data=json.dumps(data), headers=self._header, timeout=10)
        except Exception as e:
            raise e
        authid = json.loads(r.text).get("result")
        return authid


    def _configure_post_data(self, zb_post_data, itemid, history):
        zb_post_data['auth'] = self._get_authid()
        zb_post_data['params']['itemids'] = itemid
        zb_post_data['params']['history'] = history
        return zb_post_data


    def _get_server_status_by_itemid(self, itemid):
        zb_data_default = copy.deepcopy(current_app.config.get('ZABBIX_POST_DATA'))
        zb_post_data = self._configure_post_data(zb_data_default, itemid, 3)
        try:
            r = requests.post(self._url, data=json.dumps(zb_post_data), headers=self._header, timeout=10)
        except Exception as e:
            raise e
        result = json.loads(r.text).get("result")
        if result:
            return result[0].get('value')
        return '0'


    def _get_resolve_rate_by_itemid(self, itemid, limit_num):

        time_slot_minutes = int(limit_num/12)
        all_num = time_slot_minutes * 13

        zb_data_default = copy.deepcopy(current_app.config.get('ZABBIX_POST_DATA'))
        zb_post_data = self._configure_post_data(zb_data_default, itemid, 3)
        zb_post_data['params']['limit'] = all_num
        try:
            r = requests.post(self._url, data=json.dumps(zb_post_data), headers=self._header, timeout=10)
        except Exception as e:
            raise e
        results = json.loads(r.text).get("result")
        # print('xxxxx --- ' + str(len(results)))
        results_dct = OrderedDict()
        for i in range(13):
            end = time_slot_minutes*(i+1)
            if i >= 12:
                end = time_slot_minutes*(i+1) - 1
            # print(len(results))
            # print(end)
            resolving_slot = results[time_slot_minutes*i : end]
            time_flag = results[end]['clock']
            time_flag_str = datetime.fromtimestamp(int(time_flag)).strftime("%m-%d %H:%M")
            resolving_slot_amount = 0
            for ss in resolving_slot:
                resolving_slot_amount += int(ss['value'])
            results_dct[time_flag_str] = resolving_slot_amount
        
        return {'name':self._server.host, 'data':results_dct}


    def get_server_status(self):
        # itemids = [self._server.zb_process_itemid, self._server.zb_port_itemid, self._server.zb_resolve_itemid]

        return {'process':self._get_server_status_by_itemid(self._server.zb_process_itemid),
                'port':self._get_server_status_by_itemid(self._server.zb_port_itemid),
                'resolve':self._get_server_status_by_itemid(self._server.zb_resolve_itemid)
            }


    def get_resolve_rate(self, start_time, end_time):
        # time_slot = (end_time - start_time)/11
        time_slot = end_time - start_time
        total_minutes = time_slot.total_seconds()/60
        time_slot_minutes = int(total_minutes/12)
        # dns_servers = Server.query.all()  
        return self._get_resolve_rate_by_itemid(self._server.zb_resolve_rate_itemid, total_minutes)


