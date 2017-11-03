from flask_restful import Resource, marshal_with, fields
from flask import Blueprint, request, jsonify, current_app


from flask_restful import Api, Resource, url_for, reqparse, abort
from flask import current_app, g

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord
from peb_dns.models.account import Operation, ResourceType, DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.decorators import token_required, admin_required
from peb_dns import db
from peb_dns.common.util import ResourceContent
from sqlalchemy import and_, or_
from datetime import datetime


dns_role_common_parser = reqparse.RequestParser()
dns_role_common_parser.add_argument('name', type = int, location = 'json', required=True, help='role name.')
dns_role_common_parser.add_argument('privilege_ids', type = int, location = 'json', action='append', required=True)


user_fields = {
    'id': fields.String,
    'username': fields.String,
}


privilege_fields = {
    'id': fields.String,
    'name': fields.String,
    'operation': fields.String,
    'resource_type': fields.String,
    'resource_id': fields.String,
    'comment': fields.String,
}


role_fields = {
    'id': fields.String,
    'name': fields.String,
    'users': fields.List(fields.Nested(user_fields)),
    'privileges': fields.List(fields.Nested(privilege_fields))
}


class RoleList(Resource):

    method_decorators = [admin_required, token_required] 

    def __init__(self):
        self.post_reqparse = reqparse.RequestParser()
        self.post_reqparse.add_argument('name', type = int, location = 'json', required=True, help='role name.')
        super(RoleList, self).__init__()

    @marshal_with(role_fields, envelope='roles')
    def get(self):
        return DBRole.query.all()

    def post(self):
        args = self.post_reqparse.parse_args()
        role_name = args['name']
        try:
            new_role = DBRole(name=role_name)
            db.session.add(new_role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200


class Role(Resource):

    method_decorators = [admin_required, token_required]

    def __init__(self):
        self.role_common_parser = reqparse.RequestParser()
        self.role_common_parser.add_argument('privilege_ids', type = int, location = 'json', action='append', required=True)
        super(Role, self).__init__()


    def get(self, role_id):
        current_u = DBRole.query.get(role_id)
        args = self.role_common_parser.parse_args()
        return { 'message' : "哈哈哈哈哈哈" }, 200


    def put(self, role_id):
        args = self.role_common_parser.parse_args()
        privilege_ids = args['privilege_ids']
        current_role = DBRole.query.get(role_id)
        if not current_role:
            return dict(message='Failed', error="{e} 不存在！".format(e=str(role_id))), 200
        try:
            DBRolePrivilege.query.filter(DBRolePrivilege.role_id==role_id, ~DBRolePrivilege.privilege_id.in_(tuple(privilege_ids))).delete()
            for privilege_id in privilege_ids:
                rp = DBRolePrivilege.query.filter(DBRolePrivilege.role_id==role_id, DBRolePrivilege.privilege_id==privilege_id).first()
                if not rp:
                    new_role_privilege = DBRolePrivilege(role_id=role_id, privilege_id=privilege_id)
                    db.session.add(new_role_privilege)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200

    def delete(self, role_id):
        current_role = DBRole.query.get(role_id)
        if not current_role:
            return dict(message='Failed', error="{e} 不存在！".format(e=str(role_id))), 200

        related_users = current_role.users
        if related_users:
            return dict(message='Failed', error="这些用户依然关联当前角色 {e} ，请先解除关联！".format(e=str([u.username for u in related_users]))), 200

        try:
            DBUserRole.query.filter(DBUserRole.role_id==role_id).delete()
            db.sessoin.delete(current_role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200


