from flask_restful import Resource
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


dns_user_common_parser = reqparse.RequestParser()
dns_user_common_parser.add_argument('user_id', type = int, location = 'json', required=True, help='zone name.')
dns_user_common_parser.add_argument('role_ids', type = int, location = 'json', action='append', required=True)


class UserRoleList(Resource):

    method_decorators = [token_required, admin_required] 

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(UserRoleList, self).__init__()

    def get(self):
        DBUser.query.all()
        return { 'message' : "aaaaaaaaaaaaaa" }, 200

    def post(self):
        args = dns_user_common_parser.parse_args()
        role_ids = args['role_ids']
        user_id = args['user_id']
        try:
            for role_id in role_ids:
                new_user_role = DBUserRole(user_id=user_id, role_id=role_id)
                db.session.add(new_user_role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200


class UserList(Resource):

    method_decorators = [token_required, admin_required]

    # def get(self, zone_id):
    #     current_zone = DBZone.query.get(zone_id)
    #     args = dns_user_common_parser.parse_args()
    #     return { 'message' : "哈哈哈哈哈哈" }, 200

    def put(self, zone_id):
        args = dns_user_common_parser.parse_args()
        role_ids = args['role_ids']
        user_id = args['user_id']
        try:
            for role_id in role_ids:
                new_user_role = DBUserRole(user_id=user_id, role_id=role_id)
                db.session.add(new_user_role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200



    def delete(self, zone_id):
        current_zone = DBZone.query.get(zone_id)
        try:
            self._remove_zone_privileges(current_zone)
            self._delete_zone(current_zone)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200

