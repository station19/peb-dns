from flask_restful import Api, Resource, url_for, reqparse, abort
from flask import current_app, g

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog
from peb_dns.models.account import Operation, ResourceType, DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.decorators import token_required
from peb_dns import db
from peb_dns.common.util import ResourceContent
from sqlalchemy import and_, or_

dns_view_common_parser = reqparse.RequestParser()
dns_view_common_parser.add_argument('name', type = str, location = 'json', required=True, help='host')
dns_view_common_parser.add_argument('acl', type = str, location = 'json', required=True)


class DNSViewList(Resource):

    method_decorators = [token_required] 

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(DNSViewList, self).__init__()

    def get(self):
        DBView.query.all()
        return { 'message' : "aaaaaaaaaaaaaa" }, 200

    def post(self):
        args = dns_view_common_parser.parse_args()
        unique_view = DBView.query.filter_by(name=args['name']).first()
        if unique_view:
            return dict(message='Failed', error='创建失败！重复的View， 相同的名字的View已存在！！')
        new_view = DBView(**args)
        db.session.add(new_view)
        db.session.flush()
        log = DBOperationLog(operation_type='添加', operator=g.current_user.username, target_type='View', target_name=new_view.name, \
                target_id=int(new_view.id), target_detail=ResourceContent.getViewContent(new_view))
        db.session.add(log)
        try:
            view_list = db.session.query(DBView).all()
            new_view.make_view('create', view_list)
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e)))
        db.session.commit()
        return dict(message='OK'), 201

    def _add_privilege_for_view(self, new_view):
        access_privilege_name =  new_view.name + '#' + str(Operation.ACCESS)
        update_privilege_name =  new_view.name + '#' + str(Operation.UPDATE)
        delete_privilege_name =  new_view.name + '#' + str(Operation.DELETE)
        access_privilege = DBPrivilege(name=access_privilege_name, resource_type=ResourceType.ZONE, operation=Operation.ACCESS, resource_id=new_view.id)
        update_privilege = DBPrivilege(name=update_privilege_name, resource_type=ResourceType.ZONE, operation=Operation.UPDATE, resource_id=new_view.id)
        delete_privilege = DBPrivilege(name=delete_privilege_name, resource_type=ResourceType.ZONE, operation=Operation.DELETE, resource_id=new_view.id)
        db.session.add(access_privilege)
        db.session.add(update_privilege)
        db.session.add(delete_privilege)
        db.session.flush()
        admin_access =  DBRolePrivilege(role_id=1, privilege_id=access_privilege.id)
        admin_update =  DBRolePrivilege(role_id=1, privilege_id=update_privilege.id)
        admin_delete =  DBRolePrivilege(role_id=1, privilege_id=delete_privilege.id)
        db.session.add(admin_access)
        db.session.add(admin_update)
        db.session.add(admin_delete)


class DNSView(Resource):

    method_decorators = [token_required]

    def get(self, view_id):
        current_view = DBView.query.get(view_id)
        args = dns_view_common_parser.parse_args()
        return { 'message' : "哈哈哈哈哈哈" }, 200

    def put(self, view_id):
        current_view = DBView.query.get(view_id)
        args = dns_view_common_parser.parse_args()
        try:
            self._update_view(current_view, args)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200

    def delete(self, view_id):
        current_view = DBView.query.get(view_id)
        try:
            self._delete_view(current_view)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200

    def _update_view(self, view, args):
        log = DBOperationLog(operation_type='修改', operator=g.current_user.username, target_type='View', target_name=view.name, \
                target_id=int(view.id), target_detail=ResourceContent.getViewContent(view, prefix="修改前："))
        db.session.add(log)
        view.name = args['name']
        view.acl = args['acl']
        db.session.add(view)
        view_list = db.session.query(DBView).all()
        view.make_view('modify', view_list)

    def _delete_view(self, view):
        log = DBOperationLog(operation_type='删除', operator=g.current_user.username, target_type='View', target_name=view.name, \
                target_id=int(view.id), target_detail=ResourceContent.getViewContent(view))
        db.session.add(log)
        db.session.delete(view)
        view_list = db.session.query(DBView).all()
        view.make_view('delete', view_list)


