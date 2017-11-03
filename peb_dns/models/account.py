from flask import current_app, request
from peb_dns.extensions import db
from sqlalchemy import and_, or_
from werkzeug.security import generate_password_hash, check_password_hash
from .dns import DBZone, DBView, DBRecord, DBDNSServer
from datetime import datetime


class Operation(object):
    ACCESS = 0
    UPDATE = 1
    DELETE = 2


class ResourceType(object):
    SERVER = 0
    VIEW = 1
    ZONE = 2
    RECORD = 3
    USER = 4
    ROLE = 5
    PRIVILEGE = 6
    PAGE = 7
    SERVER = 8


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


    def to_json(self):
        json_user = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'cellphone': self.cellphone,
            'position': self.position,
            'location': self.location,
            'member_since': self.member_since
        }
        return json_user


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


    @property
    def roles(self):
        return db.session.query(DBRole).join(DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
            .join(DBUser, and_(DBRole.id == DBUserRole.user_id)) \
            .filter(DBUser.id == self.id).all()

    @roles.setter
    def roles(self, role_ids):
        for role_id in role_ids:
            current_user_new_role = DBUserRole(user_id=self.id, role_id=role_id)
            db.session.add(current_user_new_role)


    def can_do(self, operation, resource_type, resource_id):
        if resource_type == ResourceType.ZONE:
            r = DBZone
        elif resource_type == ResourceType.VIEW:
            r = DBView
        elif resource_type == ResourceType.RECORD:
            r = DBRecord
        elif resource_type == ResourceType.SERVER:
            r = DBDNSServer
        current_user_resources = db.session.query(r) \
            .join(DBPrivilege, and_(r.id == resource_id, r.id == DBPrivilege.resource_id, DBPrivilege.resource_type == resource_type, DBPrivilege.operation == operation)) \
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

    @property
    def users(self):
        return db.session.query(DBUser).join(DBUserRole, and_(DBUserRole.user_id == DBUser.id)) \
            .join(DBRole, and_(DBRole.id == DBUserRole.role_id)) \
            .filter(DBRole.id == self.id).all()

    @property
    def privileges(self):
        return db.session.query(DBPrivilege).join(DBRolePrivilege, and_(DBRolePrivilege.privilege_id == DBPrivilege.id)) \
            .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
            .filter(DBRole.id == self.id).all()

    @privileges.setter
    def privileges(self, privilege_ids):
        for privilege_id in privilege_ids:
            current_role_new_privilege = DBRolePrivilege(role_id=self.id, privilege_id=privilege_id)
            db.session.add(current_role_new_privilege)


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

