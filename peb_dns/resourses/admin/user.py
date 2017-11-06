from flask_restful import Resource, marshal_with, fields, marshal, reqparse
from flask import Blueprint, request, jsonify, current_app, g


from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.decorators import token_required, admin_required
from peb_dns import db
from sqlalchemy import and_, or_
from datetime import datetime


dns_user_common_parser = reqparse.RequestParser()
# dns_user_common_parser.add_argument('user_id', type = int, location = 'json', required=True, help='zone name.')
dns_user_common_parser.add_argument('role_ids', type = int, location = 'json', action='append', required=True)


role_fields = {
    'id': fields.String,
    'name': fields.String,
}

user_fields = {
    'id': fields.String,
    'username': fields.String,
    'roles': fields.List(fields.Nested(role_fields))
}

paginated_user_fields = {
    'total': fields.String,
    'users': fields.List(fields.Nested(user_fields)),
    'current_page': fields.String
}

class UserList(Resource):

    method_decorators = [admin_required, token_required] 

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(UserList, self).__init__()

    def get(self):
        args = request.args
        current_page = request.args.get('currentPage', 1, type=int)
        page_size = request.args.get('pageSize', 3, type=int)

        marshal_records = marshal(DBUser.query.order_by(DBUser.id.desc()).paginate(current_page, page_size, error_out=False).items, user_fields)
        results_wrapper = {'total': DBUser.query.count(), 'users': marshal_records, 'current_page': current_page}
        return marshal(results_wrapper, paginated_user_fields)


class User(Resource):

    method_decorators = [token_required]

    def get(self, user_id):
        current_u = DBUser.query.get(user_id)
        args = dns_user_common_parser.parse_args()
        return { 'message' : "哈哈哈哈哈哈" }, 200


    def put(self, user_id):
        args = dns_user_common_parser.parse_args()
        role_ids = args['role_ids']
        print(role_ids)
        current_u = DBUser.query.get(user_id)
        if not current_u:
            return dict(message='Failed', error="{e} 不存在！".format(e=str(user_id))), 400
        try:
            # print(DBUserRole.query.filter(DBUserRole.user_id==user_id, DBUserRole.role_id.notin_(role_ids)).all())
            for del_ur in DBUserRole.query.filter(DBUserRole.user_id==user_id, DBUserRole.role_id.notin_(role_ids)).all():
                db.session.delete(del_ur)
            for role_id in role_ids:
                ur = DBUserRole.query.filter(DBUserRole.role_id==role_id, DBUserRole.user_id==user_id).first()
                if not ur:
                    new_user_role = DBUserRole(user_id=user_id, role_id=role_id)
                    db.session.add(new_user_role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 400
        return dict(message='OK'), 200


    def delete(self, user_id):
        current_u = DBUser.query.get(user_id)
        if not current_u:
            return dict(message='Failed', error="{e} 不存在！".format(e=str(user_id))), 400
        try:
            DBUserRole.query.filter(DBUserRole.user_id==user_id).delete()
            db.sessoin.delete(current_u)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200


