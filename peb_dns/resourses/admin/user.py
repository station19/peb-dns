from flask_restful import Resource, marshal_with, fields, marshal, reqparse, abort
from flask import Blueprint, request, jsonify, current_app, g

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord, DBDNSServer
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.decorators import token_required, admin_required, permission_required, indicated_privilege_required, owner_or_admin_required, resource_exists_required
from peb_dns.common.util import getETCDclient, get_response, get_response_wrapper_fields
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING, ROLE_MAPPINGS, DefaultPrivilege
from peb_dns import db
from sqlalchemy import and_, or_
from datetime import datetime


dns_user_common_parser = reqparse.RequestParser()
dns_user_common_parser.add_argument('role_ids', 
                                type = int, 
                                location = 'json', 
                                action='append')
dns_user_common_parser.add_argument('email', 
                                type = str, 
                                location = 'json')
dns_user_common_parser.add_argument('chinese_name', 
                                type = str, 
                                location = 'json')
dns_user_common_parser.add_argument('cellphone', 
                                type = str, 
                                location = 'json')
dns_user_common_parser.add_argument('position', 
                                type = str, 
                                location = 'json')
dns_user_common_parser.add_argument('location', 
                                type = str, 
                                location = 'json')

role_fields = {
    'id': fields.Integer,
    'name': fields.String,
}


user_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'username': fields.String,
    'chinese_name': fields.String,
    'cellphone': fields.String,
    'position': fields.String,
    'location': fields.String,
    'member_since': fields.String,
    'last_seen': fields.String,
    'roles': fields.List(fields.Nested(role_fields)),
}


single_user_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'username': fields.String,
    'chinese_name': fields.String,
    'cellphone': fields.String,
    'position': fields.String,
    'location': fields.String,
    'member_since': fields.String,
    'last_seen': fields.String,
    'can_add_server': fields.Boolean,
    'can_add_view': fields.Boolean,
    'can_add_zone': fields.Boolean,
    'can_edit_bind_conf': fields.Boolean,
    'roles': fields.List(fields.Nested(role_fields)),
}


paginated_user_fields = {
    'total': fields.Integer,
    'users': fields.List(fields.Nested(user_fields)),
    'current_page': fields.Integer
}

class UserList(Resource):
    method_decorators = [admin_required, token_required] 

    def get(self):
        """Get user list."""
        args = request.args
        current_page = args.get('currentPage', 1, type=int)
        page_size = args.get('pageSize', 10, type=int)

        id = args.get('id', type=int)
        email = args.get('email', type=str)
        username = args.get('username', type=str)
        chinese_name = args.get('chinese_name', type=str)
        cellphone = args.get('cellphone', type=str)
        user_query = DBUser.query
        if id is not None:
            user_query = user_query.filter_by(id=id)
        if email is not None:
            user_query = user_query.filter_by(email=email)
        if username is not None:
            user_query = user_query.filter_by(username=username)
        if chinese_name is not None:
            user_query = user_query.filter_by(chinese_name=chinese_name)
        if cellphone is not None:
            user_query = user_query.filter_by(cellphone=cellphone)
        marshal_records = marshal(
            user_query.order_by(DBUser.id.desc()).paginate(
                current_page, 
                page_size, 
                error_out=False).items, user_fields
            )
        results_wrapper = {
            'total': user_query.count(), 
            'users': marshal_records, 
            'current_page': current_page
            }
        response_wrapper_fields = get_response_wrapper_fields(fields.Nested(paginated_user_fields))
        response_wrapper = get_response(True, '获取成功！', results_wrapper)
        return marshal(response_wrapper, response_wrapper_fields)


class User(Resource):
    method_decorators = [token_required]

    @owner_or_admin_required
    def get(self, user_id):
        """Get the detail info of the indicated user."""
        current_u = DBUser.query.get(user_id)
        if not current_u:
            return get_response(False, '用户不存在！')
        results_wrapper = marshal(current_u, single_user_fields)
        return get_response(True, '获取成功！', results_wrapper)

    @owner_or_admin_required
    def put(self, user_id):
        """Update the indicated user."""
        current_u = DBUser.query.get(user_id)
        if not current_u:
            return get_response(False, "用户不存在！")
        args = dns_user_common_parser.parse_args()
        role_ids = args.get('role_ids')
        try:
            current_u.cellphone = args.get('cellphone', '')
            current_u.chinese_name = args.get('chinese_name', '')
            current_u.email = args.get('email', '')
            current_u.location = args.get('location', '')
            current_u.position = args.get('position', '')
            db.session.add(current_u)
            if role_ids is not None:
                for del_ur in DBUserRole.query.filter(
                        DBUserRole.user_id==user_id, 
                        DBUserRole.role_id.notin_(role_ids)).all():
                    db.session.delete(del_ur)
                for role_id in role_ids:
                    ur = DBUserRole.query.filter(
                        DBUserRole.role_id==role_id, 
                        DBUserRole.user_id==user_id).first()
                    if not ur:
                        new_user_role = DBUserRole(
                                user_id=user_id, role_id=role_id)
                        db.session.add(new_user_role)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(False, '修改失败！\n{e}'.format(e=str(e)))
        return get_response(True, '修改成功！')

    @admin_required
    def delete(self, user_id):
        """Delete the indicated role."""
        current_u = DBUser.query.get(user_id)
        if not current_u:
            return get_response(False, "用户不存在！")
        try:
            DBUserRole.query.filter(
                    DBUserRole.user_id==user_id).delete()
            db.session.delete(current_u)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(False, '删除失败！\n{e}'.format(e=str(e)))
        return get_response(True, '删除成功！')


