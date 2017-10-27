from flask import current_app, request
from peb_dns.extensions import db
from sqlalchemy import and_, or_
from werkzeug.security import generate_password_hash, check_password_hash
from .dns import DBZone, DBView, DBRecord, DBDNSServer
from datetime import datetime

class DBUser(db.Model):
    __tablename__ = 'account_user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    chinese_name = db.Column(db.String(64))
    cellphone = db.Column(db.String(64))
    actived = db.Column(db.Boolean, default=False)
    position = db.Column(db.String(64))
    location = db.Column(db.String(64))
    acitve = db.Column(db.Integer)
    member_since = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)


    def can(self, privilege):

        current_user_privileges = db.session.query(DBPrivilege).join(DBRolePrivilege, and_(DBPrivilege.id == DBRolePrivilege.privilege_id, DBPrivilege.name == privilege)) \
            .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
            .join(DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
            .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
            .filter(DBUser.id == self.id).all()
        
        for current_user_privilege in current_user_privileges:
            if privilege == current_user_privilege.name:
                return True
        return False


    def is_admin(self):
        admins = db.session.query(DBRole).join(DBUserRole, and_(DBUserRole.role_id == DBRole.id, DBRole.name == "admin")) \
            .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
            .filter(DBUser.id == self.id).all()
        if admins:
            return True
        return False


    def can_access_zone(self, zone_name):
        zones = db.session.query(DBZone) \
            .join(DBPrivilege, and_(DBZone.name == zone_name, DBZone.id == DBPrivilege.resource_id, DBPrivilege.resource_type == Resource.ZONE, DBPrivilege.operation == Operation.VISIT)) \
            .join(DBRolePrivilege, and_(DBPrivilege.id == DBRolePrivilege.privilege_id)) \
            .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
            .join(DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
            .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
            .filter(DBUser.id == self.id).all()

        if zones:
            return True
        return False


    def can_update(self, resource_type, resource_id):
        if resource_type == Resource.ZONE:
            r = DBZone
        elif resource_type == Resource.VIEW:
            r = DBView
        current_user_resources = db.session.query(r) \
            .join(DBPrivilege, and_(r.id == resource_id, r.id == DBPrivilege.resource_id, DBPrivilege.resource_type == resource_type, DBPrivilege.operation == Operation.UPDATE)) \
            .join(DBRolePrivilege, and_(DBPrivilege.id == DBRolePrivilege.privilege_id)) \
            .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
            .join(DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
            .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
            .filter(DBUser.id == self.id).all()

        if current_user_resources:
            return True
        return False


    def can_delete(self, resource_type, resource_id):
        if resource_type == Resource.ZONE:
            r = DBZone
        elif resource_type == Resource.VIEW:
            r = DBView
        current_user_resources = db.session.query(r) \
            .join(DBPrivilege, and_(r.id == resource_id, r.id == DBPrivilege.resource_id, DBPrivilege.resource_type == resource_type, DBPrivilege.operation == Operation.DELETE)) \
            .join(DBRolePrivilege, and_(DBPrivilege.id == DBRolePrivilege.privilege_id)) \
            .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
            .join(DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
            .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
            .filter(DBUser.id == self.id).all()

        if current_user_resources:
            return True
        return False


class DBLocalAuth(db.Model):
    __tablename__ = 'account_local_auth'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128)) 

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class DBUserRole(db.Model):
    __tablename__ = 'account_user_role'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    role_id = db.Column(db.Integer, index=True)


class DBRole(db.Model):
    __tablename__ = 'account_role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<DBRole %r>' % self.name


class DBRolePrivilege(db.Model):
    __tablename__ = 'account_role_privilege'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, index=True)
    privilege_id = db.Column(db.Integer, index=True)


#权限表
class DBPrivilege(db.Model):
    __tablename__ = 'account_privilege'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    operation = db.Column(db.Integer)
    resource_type = db.Column(db.String(64))
    resource_id = db.Column(db.Integer, index=True)
    comment = db.Column(db.String(128))


class Operation(object):
    VISIT = 0
    UPDATE = 1
    DELETE = 2


class Resource(object):
    SERVER = 0
    VIEW = 1
    ZONE = 2
    USER = 3
    ROLE = 4
    PRIVILEGE = 5
    PAGE = 6
