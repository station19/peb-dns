from flask_restful import Api, Resource, url_for, reqparse, abort, marshal_with, fields, marshal
from flask import current_app, g, request

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog
from peb_dns.models.account import Operation, ResourceType, DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.decorators import token_required
from peb_dns import db
from peb_dns.common.util import ResourceContent
from sqlalchemy import and_, or_

dns_view_common_parser = reqparse.RequestParser()
dns_view_common_parser.add_argument('name', type = str, location = 'json', required=True, help='host')
dns_view_common_parser.add_argument('acl', type = str, location = 'json', required=True)


view_fields = {
    'id': fields.String,
    'name': fields.String,
    'acl': fields.String,
}

paginated_view_fields = {
    'total': fields.String,
    'views': fields.List(fields.Nested(view_fields)),
    'current_page': fields.String
}

class DNSViewList(Resource):

    method_decorators = [token_required] 

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(DNSViewList, self).__init__()

    def get(self):
        args = request.args
        current_page = request.args.get('currentPage', 1, type=int)
        page_size = request.args.get('pageSize', 3, type=int)

        marshal_records = marshal(DBView.query.order_by(DBView.id.desc()).paginate(current_page, page_size, error_out=False).items, view_fields)
        results_wrapper = {'total': DBView.query.count(), 'views': marshal_records, 'current_page': current_page}
        return marshal(results_wrapper, paginated_view_fields)

    def post(self):
        args = dns_view_common_parser.parse_args()
        unique_view = DBView.query.filter_by(name=args['name']).first()
        if unique_view:
            return dict(message='Failed', error='创建失败！重复的View， 相同的名字的View已存在！！'), 400
        new_view = DBView(**args)
        db.session.add(new_view)
        db.session.flush()
        log = DBOperationLog(operation_type='添加', operator=g.current_user.username, target_type='View', target_name=new_view.name, \
                target_id=int(new_view.id), target_detail=ResourceContent.getViewContent(new_view))
        db.session.add(log)
        try:
            self._add_privilege_for_view(new_view)
            view_list = db.session.query(DBView).all()
            new_view.make_view('create', view_list)
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 400
        db.session.commit()
        return dict(message='OK'), 201

    def _add_privilege_for_view(self, new_view):
        access_privilege_name =  new_view.name + '#' + str(Operation.ACCESS)
        update_privilege_name =  new_view.name + '#' + str(Operation.UPDATE)
        delete_privilege_name =  new_view.name + '#' + str(Operation.DELETE)
        access_privilege = DBPrivilege(name=access_privilege_name, resource_type=ResourceType.VIEW, operation=Operation.ACCESS, resource_id=new_view.id)
        update_privilege = DBPrivilege(name=update_privilege_name, resource_type=ResourceType.VIEW, operation=Operation.UPDATE, resource_id=new_view.id)
        delete_privilege = DBPrivilege(name=delete_privilege_name, resource_type=ResourceType.VIEW, operation=Operation.DELETE, resource_id=new_view.id)
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

        args = request.args
        current_page = request.args.get('currentPage', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)
        if view_id:
            marshal_records = marshal(DBRecord.query.filter(DBRecord.zone_id==int(zone_id)).order_by(DBRecord.id.desc()).paginate(current_page, page_size, error_out=False).items, record_fields)
            results_wrapper = {'total': DBRecord.query.filter(DBRecord.zone_id==int(zone_id)).count(), 'records': marshal_records, 'current_page': current_page}
            return marshal(results_wrapper, paginated_record_fields)

        marshal_records = marshal(DBRecord.query.order_by(DBRecord.id.desc()).paginate(current_page, page_size, error_out=False).items, record_fields)
        results_wrapper = {'total': DBRecord.query.count(), 'records': marshal_records, 'current_page': current_page}
        return marshal(results_wrapper, paginated_record_fields)


    def put(self, view_id):
        current_view = DBView.query.get(view_id)
        args = dns_view_common_parser.parse_args()
        try:
            self._update_view(current_view, args)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 400
        return dict(message='OK'), 200

    def delete(self, view_id):
        current_view = DBView.query.get(view_id)
        print(current_view)
        current_view_related_zones = current_view.zone_name_list
        if current_view_related_zones:
            return dict(message='Failed', error="{e}".format(e='当前View还与Zone有关联，请先解除关联，再进行删除操作！\n' + str(current_view_related_zones))), 400
        try:
            self._remove_view_privileges(current_view)
            self._delete_view(current_view)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 400
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


    def _remove_view_privileges(self, current_view):
        current_view_privileges_query = DBPrivilege.query.filter(DBPrivilege.resource_id==current_view.id, DBPrivilege.resource_type==ResourceType.VIEW)
        current_view_privileges = current_view_privileges_query.all()
        for view_privilege in current_view_privileges:
            DBRolePrivilege.query.filter(DBRolePrivilege.privilege_id == view_privilege.id).delete()
        current_view_privileges_query.delete()

