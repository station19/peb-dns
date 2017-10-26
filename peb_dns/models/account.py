from flask import current_app, request
from peb_dns.extensions import db
from sqlalchemy import and_, or_
from werkzeug.security import generate_password_hash, check_password_hash
from .dns import Zone, View, Record, Server
from datetime import datetime

class User(db.Model):
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

        current_user_privileges = db.session.query(Privilege).join(RolePrivilege, and_(Privilege.id == RolePrivilege.privilege_id, Privilege.name == privilege)) \
            .join(Role, and_(Role.id == RolePrivilege.role_id)) \
            .join(UserRole, and_(UserRole.role_id == Role.id)) \
            .join(User, and_(User.id == UserRole.user_id)) \
            .filter(User.id == self.id).all()
        
        for current_user_privilege in current_user_privileges:
            if privilege == current_user_privilege.name:
                return True
        return False


    def is_admin(self):
        admins = db.session.query(Role).join(UserRole, and_(UserRole.role_id == Role.id, Role.name == "admin")) \
            .join(User, and_(User.id == UserRole.user_id)) \
            .filter(User.id == self.id).all()
        if admins:
            return True
        return False


    def can_access_zone(self, zone_name):
        zones = db.session.query(Zone) \
            .join(Privilege, and_(Zone.name == zone_name, Zone.id == Privilege.resource_id, Privilege.resource_type == Resource.ZONE, Privilege.operation == Operation.VISIT)) \
            .join(RolePrivilege, and_(Privilege.id == RolePrivilege.privilege_id)) \
            .join(Role, and_(Role.id == RolePrivilege.role_id)) \
            .join(UserRole, and_(UserRole.role_id == Role.id)) \
            .join(User, and_(User.id == UserRole.user_id)) \
            .filter(User.id == self.id).all()

        if zones:
            return True
        return False


    def can_update(self, resource_type, resource_id):
        if resource_type == Resource.ZONE:
            r = Zone
        elif resource_type == Resource.VIEW:
            r = View
        current_user_resources = db.session.query(r) \
            .join(Privilege, and_(r.id == resource_id, r.id == Privilege.resource_id, Privilege.resource_type == resource_type, Privilege.operation == Operation.UPDATE)) \
            .join(RolePrivilege, and_(Privilege.id == RolePrivilege.privilege_id)) \
            .join(Role, and_(Role.id == RolePrivilege.role_id)) \
            .join(UserRole, and_(UserRole.role_id == Role.id)) \
            .join(User, and_(User.id == UserRole.user_id)) \
            .filter(User.id == self.id).all()

        if current_user_resources:
            return True
        return False


    def can_delete(self, resource_type, resource_id):
        if resource_type == Resource.ZONE:
            r = Zone
        elif resource_type == Resource.VIEW:
            r = View
        current_user_resources = db.session.query(r) \
            .join(Privilege, and_(r.id == resource_id, r.id == Privilege.resource_id, Privilege.resource_type == resource_type, Privilege.operation == Operation.DELETE)) \
            .join(RolePrivilege, and_(Privilege.id == RolePrivilege.privilege_id)) \
            .join(Role, and_(Role.id == RolePrivilege.role_id)) \
            .join(UserRole, and_(UserRole.role_id == Role.id)) \
            .join(User, and_(User.id == UserRole.user_id)) \
            .filter(User.id == self.id).all()

        if current_user_resources:
            return True
        return False


class LocalAuth(db.Model):
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


class UserRole(db.Model):
    __tablename__ = 'account_user_role'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    role_id = db.Column(db.Integer, index=True)


class Role(db.Model):
    __tablename__ = 'account_role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<Role %r>' % self.name


class RolePrivilege(db.Model):
    __tablename__ = 'account_role_privilege'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, index=True)
    privilege_id = db.Column(db.Integer, index=True)


#权限表
class Privilege(db.Model):
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
