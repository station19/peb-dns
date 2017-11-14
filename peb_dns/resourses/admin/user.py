from flask_restful import Resource, marshal_with, fields, marshal, reqparse, abort
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


# privilege_fields = {
#     'id': fields.Integer,
#     'name': fields.String,
#     'operation': fields.Integer,
#     'resource_type': fields.Integer,
#     'resource_id': fields.Integer,
#     'comment': fields.String,
# }

# role_fields = {
#     'id': fields.Integer,
#     'name': fields.String,
#     'privileges': fields.List(fields.Nested(privilege_fields)),
# }


role_fields = {
    'id': fields.Integer,
    'name': fields.String,
}

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'chinese_name': fields.String,
    'cellphone': fields.String,
    'position': fields.String,
    'location': fields.String,
    'member_since': fields.String,
    'last_seen': fields.String,
    'roles': fields.List(fields.Nested(role_fields)),
}

paginated_user_fields = {
    'total': fields.Integer,
    'users': fields.List(fields.Nested(user_fields)),
    'current_page': fields.Integer
}

class UserList(Resource):

    method_decorators = [admin_required, token_required] 

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(UserList, self).__init__()

    def get(self):
        args = request.args
        current_page = args.get('currentPage', 1, type=int)
        page_size = args.get('pageSize', 10, type=int)

        id = args.get('id', type=int)
        email = args.get('email', type=str)
        username = args.get('username', type=str)
        chinese_name = args.get('chinese_name', type=str)
        cellphone = args.get('cellphone', type=str)
        user_query = DBUser.query
        if id:
            user_query = user_query.filter_by(id=id)
        if email:
            user_query = user_query.filter_by(email=email)
        if username:
            user_query = user_query.filter_by(username=username)
        if chinese_name:
            user_query = user_query.filter_by(chinese_name=chinese_name)
        if cellphone:
            user_query = user_query.filter_by(cellphone=cellphone)

        marshal_records = marshal(user_query.order_by(DBUser.id.desc()).paginate(current_page, page_size, error_out=False).items, user_fields)
        results_wrapper = {'total': user_query.count(), 'users': marshal_records, 'current_page': current_page}
        return marshal(results_wrapper, paginated_user_fields)


class User(Resource):

    method_decorators = [token_required]

    @marshal_with(user_fields)
    def get(self, user_id):
        current_u = DBUser.query.get(user_id)
        if not current_u:
            abort(404)
        return current_u
        # return { 'message' : "哈哈哈哈哈哈" }, 200

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
            db.session.delete(current_u)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200


