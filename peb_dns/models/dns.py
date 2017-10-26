from flask import current_app, request
from peb_dns.extensions import db
from sqlalchemy import and_, or_
from datetime import datetime
from collections import OrderedDict
import jwt
import hashlib
import copy

ZONE_GROUP_MAPPING = {
    0:"外部域名",
    1:"内部域名",
    2:"劫持域名"
}

class View(db.Model):
    __tablename__ = 'dns_view'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    acl = db.Column(db.Text())
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)

    def __repr__(self):
        return '<View %r>' % self.name


class ViewZone(db.Model):
    __tablename__ = 'dns_view_zone'
    id = db.Column(db.Integer, primary_key=True)
    view_id = db.Column(db.Integer, index=True)
    zone_id = db.Column(db.Integer, index=True)
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)

class Zone(db.Model):
    __tablename__ = 'dns_zone'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    zone_group = db.Column(db.Integer)
    zone_type = db.Column(db.String(64))
    forwarders = db.Column(db.String(64))
    records = db.relationship('Record', backref='zone', lazy='dynamic')
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)


    @staticmethod
    def get_splitted_zones():
        zone_query = db.session.query(Zone).join(Privilege, and_(Zone.id == Privilege.resource_id, Privilege.resource_type == Resource.ZONE, Privilege.operation == Operation.VISIT)) \
            .join(RolePrivilege, and_(Privilege.id == RolePrivilege.privilege_id)) \
            .join(Role, and_(Role.id == RolePrivilege.role_id)) \
            .join(UserRole, and_(UserRole.role_id == Role.id)) \
            .join(User, and_(User.id == UserRole.user_id)) \
            .filter(User.id == current_user.id)
        inner_zones = [{'item_name':zone.name, 'url':'/dns/inner/'+zone.name.replace('.', '_')} for zone in zone_query.filter(Zone.is_inner == 1).all()]
        intercepted_zones = [{'item_name':zone.name, 'url':'/dns/intercepted/'+zone.name.replace('.', '_')} for zone in zone_query.filter(Zone.is_inner == 2).all()]
        outter_zones = [{'item_name':zone.name, 'url':'/dns/outter/'+zone.name.replace('.', '_')} for zone in zone_query.filter(Zone.is_inner == 0).all()]

        zone_groups = [{'title':'内部域名', 'items':inner_zones}, \
            {'title':'劫持域名', 'items':intercepted_zones},
            {'title':'外部域名', 'items':outter_zones}
        ]
        
        return zone_groups


class Record(db.Model):
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
    zone_id = db.Column(db.Integer, db.ForeignKey('dns_zones.id'))
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)


class Server(db.Model):
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


class OperationLog(db.Model):
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

