from flask_restful import Resource, marshal_with, fields, marshal, reqparse, abort
from flask import Blueprint, request, jsonify, current_app, g

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.util import getETCDclient, get_response, get_response_wrapper_fields
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING, ROLE_MAPPINGS, DefaultPrivilege
from peb_dns.common.decorators import token_required, admin_required, resource_exists_required
from peb_dns import db
from sqlalchemy import and_, or_
from datetime import datetime
from peb_dns.common.request_code import RequestCode

privilege_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'operation': fields.Integer,
    'resource_type': fields.Integer,
    'resource_id': fields.Integer,
    'comment': fields.String,
}


paginated_privilege_fields = {
    'total': fields.Integer,
    'privileges': fields.List(fields.Nested(privilege_fields)),
    'current_page': fields.Integer
}


class PrivilegeList(Resource):
    method_decorators = [admin_required, token_required] 

    def get(self):
        """Get privilege list."""
        args = request.args
        current_page = args.get('currentPage', 1, type=int)
        page_size = args.get('pageSize', 10, type=int)
        role_id = args.get('role_id', type=int)

        id = args.get('id', type=int)
        name = args.get('name', type=str)
        operation = args.get('operation', type=int)
        resource_type = args.get('resource_type', type=int)
        resource_id = args.get('resource_id', type=int)
        privilege_query = DBPrivilege.query
        if id is not None:
            privilege_query = privilege_query.filter_by(id=id)
        if name is not None:
            privilege_query = privilege_query.filter(DBPrivilege.name.like('%'+name+'%'))
        if operation is not None:
            privilege_query = privilege_query.filter_by(operation=operation)
        if resource_type is not None:
            privilege_query = privilege_query.filter_by(resource_type=resource_type)
        if resource_id is not None:
            privilege_query = privilege_query.filter_by(resource_id=resource_id)
        if role_id is not None:
            privilege_query = privilege_query.join(
                DBRolePrivilege, and_(DBRolePrivilege.privilege_id == DBPrivilege.id)) \
                    .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
                    .filter(DBRole.id == role_id)

        marshal_records = marshal(
            privilege_query.order_by(DBPrivilege.id.desc()).paginate(
                current_page, 
                page_size, 
                error_out=False
            ).items, privilege_fields)
        results_wrapper = {
            'total': privilege_query.count(), 
            'privileges': marshal_records, 
            'current_page': current_page
            }
        response_wrapper_fields = get_response_wrapper_fields(fields.Nested(paginated_privilege_fields))
        response_wrapper = get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)
        return marshal(response_wrapper, response_wrapper_fields)

    def post(self):
        """Create new privilege."""        
        args = request.json
        privilege_name = args['name']
        operation = args.get('operation') if args.get('operation') != '' else 100
        resource_type = args.get('resource_type') if args.get('resource_type') != '' else 100
        resource_id = args.get('resource_id') if args.get('resource_id') != '' else 0
        comment = args.get('comment') if args.get('comment') else ''
        # print(privilege_name, operation, resource_type, resource_id, comment)
        uniq_privilege = DBPrivilege.query.filter_by(name=privilege_name).first()
        if uniq_privilege:
            return get_response(RequestCode.OTHER_FAILED,  "{e} 权限名已存在！".format(e=str(uniq_privilege.name)))
        try:
            new_privilege = DBPrivilege(
                name=privilege_name, 
                operation=operation, 
                resource_type=resource_type, 
                resource_id=resource_id, 
                comment=comment
                )
            db.session.add(new_privilege)
            db.session.flush()
            new_rp = DBRolePrivilege(
                role_id=1, 
                privilege_id=new_privilege.id
                )
            db.session.add(new_rp)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '创建失败！')
        return get_response(RequestCode.SUCCESS, '创建成功！')


class Privilege(Resource):
    method_decorators = [admin_required, token_required]

    # def __init__(self):
    #     self.role_common_parser = reqparse.RequestParser()
    #     self.role_common_parser.add_argument(
    #         'privilege_ids', 
    #         type = int, 
    #         location = 'json', 
    #         action='append', 
    #         required=True
    #         )
    #     super(Privilege, self).__init__()

    @resource_exists_required(ResourceType.PRIVILEGE)
    def get(self, privilege_id):
        """Get the detail info of the indicated privilege."""
        current_p = DBPrivilege.query.get(privilege_id)
        results_wrapper = marshal(current_p, privilege_fields)
        return get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)

    @resource_exists_required(ResourceType.PRIVILEGE)
    def put(self, privilege_id):
        """Update the indicated privilege."""
        args = request.json
        privilege_name = args['name']
        operation = args.get('operation') if args.get('operation') != '' else 100
        resource_type = args.get('resource_type') if args.get('resource_type') != '' else 100
        resource_id = args.get('resource_id') if args.get('resource_id') != '' else 0
        comment = args.get('comment') if args.get('comment') else ''
        current_privilege = DBPrivilege.query.get(privilege_id)
        uniq_privilege = DBPrivilege.query.filter(
            DBPrivilege.name==privilege_name, 
            DBPrivilege.id!=privilege_id
            ).first()
        if uniq_privilege:
            return get_response(RequestCode.OTHER_FAILED,  "{e} 权限名已存在！".format(e=str(uniq_privilege.name)))
        try:
            current_privilege.name = privilege_name
            current_privilege.operation = operation
            current_privilege.resource_type = resource_type
            current_privilege.resource_id = resource_id
            current_privilege.comment = comment
            db.session.add(current_privilege)
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '修改失败！')
        return get_response(RequestCode.SUCCESS, '修改成功！')

    @resource_exists_required(ResourceType.PRIVILEGE)
    def delete(self, privilege_id):
        """Delete the indicated privilege."""
        current_privilege = DBPrivilege.query.get(privilege_id)
        try:
            db.session.delete(current_privilege)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '修改失败！')
        return get_response(RequestCode.SUCCESS, '修改成功！')


