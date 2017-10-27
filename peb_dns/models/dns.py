from flask import current_app, request
from peb_dns.extensions import db
from sqlalchemy.sql import and_, or_, not_
from datetime import datetime
from collections import OrderedDict
from jinja2 import Template
import jwt
import hashlib
import copy
import requests
import etcd
import time
from peb_dns.common.util import getETCDclient


ZONE_GROUP_MAPPING = {
    0:"外部域名",
    1:"内部域名",
    2:"劫持域名"
}


class DBView(db.Model):
    __tablename__ = 'dns_view'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    acl = db.Column(db.Text())
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)

    def __repr__(self):
        return '<DBView %r>' % self.name

    def make_view(self, action, view_list):
        prevExist = True
        if action == 'create':
            prevExist = False

        etcd_client = getETCDclient()

        if action == 'del':
            view_base_dir = current_app.config.get('ETCD_BASE_DIR') + self.name
            etcd_client.delete(view_base_dir, recursive=True)
            time.sleep(0.2)
            return

        if action == 'create':
            view_zone_conf = current_app.config.get('ETCD_BASE_DIR') + self.name + '/view.conf'
            view_zone_conf_content = Template(current_app.config.get('VIEW_TEMPLATE')).render(view_name=self.name)
            etcd_client.write(view_zone_conf, view_zone_conf_content, prevExist=prevExist)
            time.sleep(0.2)   #连续几个提交速度过快，etcd server检测不到提交

            view_define_conf_content = Template(current_app.config.get('VIEW_DEFINE_TEMPLATE')).render(view_list=view_list)
            print(current_app.config.get('VIEW_DEFINE_CONF'))
            print(view_define_conf_content)
            etcd_client.write(current_app.config.get('VIEW_DEFINE_CONF'), view_define_conf_content, prevExist=True)
            time.sleep(0.2)

        acl_conf = current_app.config.get('ETCD_BASE_DIR') + self.name + '/acl.conf'
        acl_conf_content = Template(current_app.config.get('ACL_TEMPLATE')).render(view_name=self.name, ip_list=self.acl.split())
        etcd_client.write(acl_conf, acl_conf_content, prevExist=prevExist)
        time.sleep(0.2)


class DBViewZone(db.Model):
    __tablename__ = 'dns_view_zone'
    id = db.Column(db.Integer, primary_key=True)
    view_id = db.Column(db.Integer, index=True)
    zone_id = db.Column(db.Integer, index=True)
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)


class DBZone(db.Model):
    __tablename__ = 'dns_zone'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    zone_group = db.Column(db.Integer)
    zone_type = db.Column(db.String(64))
    forwarders = db.Column(db.String(64))
    records = db.relationship('DBRecord', backref='zone', lazy='dynamic')
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)


    # @staticmethod
    # def get_splitted_zones():
    #     zone_query = db.session.query(DBZone).join(DBPrivilege, and_(DBZone.id == DBPrivilege.resource_id, DBPrivilege.resource_type == Resource.ZONE, DBPrivilege.operation == Operation.VISIT)) \
    #         .join(DBRolePrivilege, and_(DBPrivilege.id == DBRolePrivilege.privilege_id)) \
    #         .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
    #         .join(DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
    #         .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
    #         .filter(DBUser.id == g.current_user.id)
    #     inner_zones = [{'item_name':zone.name, 'url':'/dns/inner/'+zone.name.replace('.', '_')} for zone in zone_query.filter(DBZone.is_inner == 1).all()]
    #     intercepted_zones = [{'item_name':zone.name, 'url':'/dns/intercepted/'+zone.name.replace('.', '_')} for zone in zone_query.filter(DBZone.is_inner == 2).all()]
    #     outter_zones = [{'item_name':zone.name, 'url':'/dns/outter/'+zone.name.replace('.', '_')} for zone in zone_query.filter(DBZone.is_inner == 0).all()]

    #     zone_groups = [{'title':'内部域名', 'items':inner_zones}, \
    #         {'title':'劫持域名', 'items':intercepted_zones},
    #         {'title':'外部域名', 'items':outter_zones}
    #     ]
        
    #     return zone_groups


class DBRecord(db.Model):
    __tablename__ = 'dns_record'
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(64), index=True)
    record_type = db.Column(db.String(64))
    ttl = db.Column(db.String(64))
    value = db.Column(db.String(64))
    zone_name = db.Column(db.String(64), default='')
    comment = db.Column(db.String(64))
    creator = db.Column(db.String(64))
    status = db.Column(db.String(64), default='enabled')
    enabled = db.Column(db.String(64), default='1')
    alive = db.Column(db.String(64), default='ON')
    zone_id = db.Column(db.Integer, db.ForeignKey('dns_zone.id'))
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)


class DBDNSServer(db.Model):
    __tablename__ = 'dns_server'
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(64), index=True)
    ip = db.Column(db.String(64))
    env = db.Column(db.String(64))
    dns_server_type = db.Column(db.String(64))
    status = db.Column(db.String(64), default='INITING')
    zb_process_itemid = db.Column(db.String(64))
    zb_port_itemid = db.Column(db.String(64))
    zb_resolve_itemid = db.Column(db.String(64))
    zb_resolve_rate_itemid = db.Column(db.String(64))
    server_log = db.Column(db.Text())
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)

    def to_json(self):
        json_server = {
            'id': self.id,
            'host': self.host,
            'ip': self.ip,
            'env': self.env,
            'dns_type': self.dns_type,
            'status': self.status,
            'logs': self.logs
        }
        return json_server


class DBOperationLog(db.Model):
    __tablename__ = 'dns_operation_log'
    id = db.Column(db.Integer, primary_key=True)
    operation_time = db.Column(db.DateTime(), default=datetime.now)
    operation_type = db.Column(db.String(64))
    operator = db.Column(db.String(64))
    target_type = db.Column(db.String(64))
    target_name = db.Column(db.String(64))
    target_id = db.Column(db.String(64))
    target_detail = db.Column(db.Text())
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)

