from flask_restful import Resource, marshal_with, fields, marshal, reqparse, abort
from flask import Blueprint, request, jsonify, current_app, g

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.decorators import token_required, admin_required
from peb_dns import db
from sqlalchemy import and_, or_
from datetime import datetime


dns_privilege_common_parser = reqparse.RequestParser()
dns_privilege_common_parser.add_argument('name', type = str, location = 'json', required=True, help='role name.')
dns_privilege_common_parser.add_argument('operation', type = int, location = 'json', required=True)
dns_privilege_common_parser.add_argument('resource_type', type = int, location = 'json', required=True, help='role name.')
dns_privilege_common_parser.add_argument('resource_id', type = int, location = 'json', required=True)
dns_privilege_common_parser.add_argument('comment', type = str, location = 'json')


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

    def __init__(self):
        # self.post_reqparse = reqparse.RequestParser()
        # self.post_reqparse.add_argument('name', type = str, location = 'json', required=True)
        super(PrivilegeList, self).__init__()

    def get(self):
        args = request.args
        current_page = request.args.get('currentPage', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)
        role_id = request.args.get('role_id', type=int)

        privilege_query = db.session.query(DBPrivilege)
        if role_id:
            privilege_query = privilege_query.join(DBRolePrivilege, and_(DBRolePrivilege.privilege_id == DBPrivilege.id)) \
            .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
            .filter(DBRole.id == role_id)

        marshal_records = marshal(privilege_query.order_by(DBPrivilege.id.desc()).paginate(current_page, page_size, error_out=False).items, privilege_fields)
        results_wrapper = {'total': privilege_query.count(), 'privileges': marshal_records, 'current_page': current_page}
        return marshal(results_wrapper, paginated_privilege_fields)

    def post(self):
        
        args = dns_privilege_common_parser.parse_args()
        privilege_name = args['name']
        operation = args['operation']
        resource_type = args['resource_type']
        resource_id = args['resource_id']
        comment = args.get('comment', '')
        uniq_privilege = DBPrivilege.query.filter_by(name=privilege_name).first()
        if uniq_privilege:
            return dict(message='Failed', error="{e} 已存在！".format(e=str(uniq_privilege.name))), 400
        try:
            new_privilege = DBPrivilege(name=privilege_name, operation=operation, resource_type=resource_type, resource_id=resource_id, comment=comment)
            db.session.add(new_privilege)
            db.session.flush()
            new_rp = DBRolePrivilege(role_id=1, privilege_id=new_privilege.id)
            db.session.add(new_rp)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 400
        return dict(message='OK'), 200


class Privilege(Resource):

    method_decorators = [admin_required, token_required]

    def __init__(self):
        self.role_common_parser = reqparse.RequestParser()
        self.role_common_parser.add_argument('privilege_ids', type = int, location = 'json', action='append', required=True)
        super(Privilege, self).__init__()

    @marshal_with(privilege_fields)
    def get(self, privilege_id):
        current_p = DBPrivilege.query.get(privilege_id)
        if not current_p:
            abort(404)
        # args = self.role_common_parser.parse_args()
        # return { 'message' : "哈哈哈哈哈哈" }, 200
        return current_p


    def put(self, privilege_id):
        current_privilege = DBPrivilege.query.get(privilege_id)
        if not current_privilege:
            return dict(message='Failed', error="{e} 不存在！".format(e=str(privilege_id))), 400
        args = dns_privilege_common_parser.parse_args()

        privilege_name = args['name']
        operation = args['operation']
        resource_type = args['resource_type']
        resource_id = args['resource_id']
        comment = args.get('comment', '')
        try:
            current_privilege.name = privilege_name
            current_privilege.operation = operation
            current_privilege.resource_type = resource_type
            current_privilege.resource_id = resource_id
            current_privilege.comment = comment
            db.session.add(current_privilege)
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 400
        return dict(message='OK'), 200


    def delete(self, privilege_id):
        current_privilege = DBPrivilege.query.get(privilege_id)
        if not current_privilege:
            return dict(message='Failed', error="{e} 不存在！".format(e=str(privilege_id))), 400
        try:
            db.session.delete(current_privilege)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 400
        return dict(message='OK'), 200


