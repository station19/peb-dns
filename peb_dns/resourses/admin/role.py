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
from peb_dns.common.request_code import RequestCode


dns_role_common_parser = reqparse.RequestParser()
dns_role_common_parser.add_argument('name', 
                                type = str, 
                                location = 'json', 
                                required=True, 
                                help='role name.')
dns_role_common_parser.add_argument('privilege_ids', 
                                type = int, 
                                location = 'json', 
                                action='append', 
                                required=True)


user_fields = {
    'id': fields.Integer,
    'username': fields.String,
}


privilege_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'operation': fields.Integer,
    'resource_type': fields.Integer,
    'resource_id': fields.Integer,
    'comment': fields.String,
}


role_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'privileges': fields.List(fields.Nested(privilege_fields))
}


paginated_role_fields = {
    'total': fields.Integer,
    'roles': fields.List(fields.Nested(role_fields)),
    'current_page': fields.Integer
}


class RoleList(Resource):
    method_decorators = [admin_required, token_required] 

    def get(self):
        """Get role list."""
        args = request.args
        current_page = args.get('currentPage', 1, type=int)
        page_size = args.get('pageSize', 10, type=int)
        user_id = args.get('user_id', type=int)

        id = args.get('id', type=int)
        name = args.get('name', type=str)
        role_query = DBRole.query
        if id is not None:
            role_query = role_query.filter_by(id=id)
        if name is not None:
            role_query = role_query.filter_by(name=name)
        if user_id is not None:
            role_query = role_query \
                .join(DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
                .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
                .filter(DBUser.id == user_id)
        
        marshal_records = marshal(
                role_query.order_by(DBRole.id.desc()).paginate(
                    current_page, 
                    page_size, 
                    error_out=False).items, role_fields)
        results_wrapper = {
            'total': role_query.count(), 
            'roles': marshal_records, 
            'current_page': current_page
            }
        response_wrapper_fields = get_response_wrapper_fields(fields.Nested(paginated_role_fields))
        response_wrapper = get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)
        return marshal(response_wrapper, response_wrapper_fields)
    
    def post(self):
        """Create new role."""
        args = dns_role_common_parser.parse_args()
        role_name = args['name']
        privilege_ids = args['privilege_ids']
        try:
            new_role = DBRole(name=role_name)
            db.session.add(new_role)
            db.session.flush()
            for privilege_id in privilege_ids:
                new_rp = DBRolePrivilege(
                    role_id=new_role.id, privilege_id=privilege_id)
                db.session.add(new_rp)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '修改失败！\n{e}'.format(e=str(e)))
        return get_response(RequestCode.SUCCESS, '修改成功！')


class Role(Resource):
    method_decorators = [admin_required, token_required]

    def get(self, role_id):
        """Get the detail info of the indicated role."""
        current_role = DBRole.query.get(role_id)
        if not current_role:
            return get_response(RequestCode.OTHER_FAILED,  '角色不存在！')
        results_wrapper = marshal(current_role, role_fields)
        return get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)

    def put(self, role_id):
        """Update the indicated role."""
        args = dns_role_common_parser.parse_args()
        role_name = args['name']
        privilege_ids = args['privilege_ids']
        current_role = DBRole.query.get(role_id)
        if not current_role:
            return get_response(RequestCode.OTHER_FAILED,  "角色不存在！")
        try:
            current_role.name = role_name
            for del_rp in DBRolePrivilege.query.filter(
                    DBRolePrivilege.role_id==role_id, 
                    DBRolePrivilege.privilege_id.notin_(privilege_ids)
                    ).all():
                db.session.delete(del_rp)
            for privilege_id in privilege_ids:
                rp = DBRolePrivilege.query.filter(
                    DBRolePrivilege.role_id==role_id, 
                    DBRolePrivilege.privilege_id==privilege_id
                    ).first()
                if not rp:
                    new_role_privilege = DBRolePrivilege(
                            role_id=role_id, privilege_id=privilege_id)
                    db.session.add(new_role_privilege)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '修改失败！\n{e}'.format(e=str(e)))
        return get_response(RequestCode.SUCCESS, '修改成功！')

    def delete(self, role_id):
        """Delete the indicated role."""
        current_role = DBRole.query.get(role_id)
        if not current_role:
            return get_response(RequestCode.OTHER_FAILED,  "角色不存在！")
        related_users = current_role.users
        if related_users:
            return get_response(RequestCode.OTHER_FAILED,  "这些用户依然关联当前角色 {e} ，请先解除关联！"
                    .format(e=str([u.username for u in related_users])))
        try:
            DBUserRole.query.filter(DBUserRole.role_id==role_id).delete()
            db.session.delete(current_role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '删除失败！\n{e}'.format(e=str(e)))
        return get_response(RequestCode.SUCCESS, '删除成功！')


