from flask_restful import Api, Resource, url_for, reqparse, abort, marshal_with, fields, marshal
from flask import current_app, g, request

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord, DBDNSServer
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.decorators import token_required, admin_required, permission_required, indicated_privilege_required, resource_exists_required
from peb_dns.common.util import getETCDclient, get_response, get_response_wrapper_fields
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING, ROLE_MAPPINGS, DefaultPrivilege
from peb_dns.common.util import DNSPod
from peb_dns import db
from sqlalchemy import and_, or_
from peb_dns.common.request_code import RequestCode

dns_view_common_parser = reqparse.RequestParser()
dns_view_common_parser.add_argument('name', 
                                    type = str, 
                                    location = 'json', 
                                    required=True, 
                                    help='host')
dns_view_common_parser.add_argument('acl', 
                                    type = str, 
                                    location = 'json', 
                                    required=True)


view_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'acl': fields.String,
    'can_update': fields.Boolean,
    'can_delete': fields.Boolean
}

paginated_view_fields = {
    'total': fields.Integer,
    'views': fields.List(fields.Nested(view_fields)),
    'current_page': fields.Integer
}

class DNSViewList(Resource):
    method_decorators = [token_required] 

    def get(self):
        """Get view list."""
        args = request.args
        zone_id = args.get('zone_id', type=int)
        current_page = request.args.get('currentPage', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)

        id = args.get('id', type=int)
        name = args.get('name', type=str)
        view_query = DBView.query
        if id is not None:
            view_query = view_query.filter_by(id=id)
        if name is not None:
            view_query = view_query.filter(DBView.name.like('%'+name+'%'))
        if zone_id is not None:
            current_zone = DBZone.query.get(zone_id)
            if current_zone.zone_group == 0:
                print(DNSPod.getDNSPodLines(current_zone.name))
                return DNSPod.getDNSPodLines(current_zone.name)
            view_query = view_query.join(
                DBViewZone, and_(DBViewZone.view_id == DBView.id)) \
                .join(DBZone, and_(DBZone.id == DBViewZone.zone_id)) \
                .filter(DBZone.id == int(zone_id))
        marshal_records = marshal(
                view_query.order_by(DBView.id.desc()).paginate(
                    current_page, 
                    page_size, 
                    error_out=False).items, view_fields)
        results_wrapper = {
                'total': view_query.count(), 
                'views': marshal_records, 
                'current_page': current_page
                }
        response_wrapper_fields = get_response_wrapper_fields(fields.Nested(paginated_view_fields))
        response_wrapper = get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)
        return marshal(response_wrapper, response_wrapper_fields)

    @indicated_privilege_required(DefaultPrivilege.VIEW_ADD)
    def post(self):
        """Create new view."""
        args = dns_view_common_parser.parse_args()
        unique_view = DBView.query.filter_by(name=args['name']).first()
        if unique_view:
            return get_response(RequestCode.OTHER_FAILED,  '创建失败！重复的View， 相同的名字的View已存在！！')
        new_view = DBView(**args)
        db.session.add(new_view)
        db.session.flush()
        log = DBOperationLog(
            operation_type='添加', 
            operator=g.current_user.username, 
            target_type='View', 
            target_name=new_view.name,
            target_id=int(new_view.id), 
            target_detail=new_view.get_content_str()
            )
        db.session.add(log)
        try:
            self._add_privilege_for_view(new_view)
            view_list = db.session.query(DBView).all()
            new_view.make_view('create', view_list)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  "{e}".format(e=str(e)))
        return get_response(RequestCode.SUCCESS, '创建成功！')

    def _add_privilege_for_view(self, new_view):
        """Add privilege for the new view."""
        access_privilege_name =  'VIEW#' + new_view.name + \
                    '#' + OPERATION_STR_MAPPING[Operation.ACCESS]
        update_privilege_name =  'VIEW#' + new_view.name + \
                    '#' + OPERATION_STR_MAPPING[Operation.UPDATE]
        delete_privilege_name =  'VIEW#' + new_view.name + \
                    '#' + OPERATION_STR_MAPPING[Operation.DELETE]
        access_privilege = DBPrivilege(
                            name=access_privilege_name, 
                            resource_type=ResourceType.VIEW, 
                            operation=Operation.ACCESS, 
                            resource_id=new_view.id
                            )
        update_privilege = DBPrivilege(
                            name=update_privilege_name, 
                            resource_type=ResourceType.VIEW, 
                            operation=Operation.UPDATE, 
                            resource_id=new_view.id
                            )
        delete_privilege = DBPrivilege(
                            name=delete_privilege_name, 
                            resource_type=ResourceType.VIEW, 
                            operation=Operation.DELETE, 
                            resource_id=new_view.id
                            )
        db.session.add(access_privilege)
        db.session.add(update_privilege)
        db.session.add(delete_privilege)
        db.session.flush()
        for role in ['admin', 'view_admin', 'view_guest']:
            role_access =  DBRolePrivilege(
                                role_id=ROLE_MAPPINGS[role],
                                privilege_id=access_privilege.id)
            db.session.add(role_access)
            if role not in ['view_guest']:
                role_update =  DBRolePrivilege(
                                    role_id=ROLE_MAPPINGS[role],
                                    privilege_id=update_privilege.id)
                role_delete =  DBRolePrivilege(
                                    role_id=ROLE_MAPPINGS[role],
                                    privilege_id=delete_privilege.id)
                db.session.add(role_update)
                db.session.add(role_delete)


class DNSView(Resource):
    method_decorators = [token_required]

    @resource_exists_required(ResourceType.VIEW)
    @permission_required(ResourceType.VIEW, Operation.ACCESS)
    def get(self, view_id):
        """Get the detail info of the single view."""
        current_view = DBView.query.get(view_id)
        results_wrapper = marshal(current_view, view_fields)
        return get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)

    @resource_exists_required(ResourceType.VIEW)
    @permission_required(ResourceType.VIEW, Operation.UPDATE)
    def put(self, view_id):
        """Update the indicated view."""
        current_view = DBView.query.get(view_id)
        args = dns_view_common_parser.parse_args()
        try:
            self._update_view(current_view, args)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '修改失败！\n{e}'.format(e=str(e)))
        return get_response(RequestCode.SUCCESS, '修改成功！')

    @resource_exists_required(ResourceType.VIEW)
    @permission_required(ResourceType.VIEW, Operation.DELETE)
    def delete(self, view_id):
        """Delete the indicated view."""
        current_view = DBView.query.get(view_id)
        current_view_related_zones = current_view.zone_name_list
        if current_view_related_zones:
            return get_response(RequestCode.OTHER_FAILED,  "{e}".format(
                            e='当前View还与Zone有关联，请先解除关联，再进行删除操作！\n' \
                            + str(current_view_related_zones)))
        try:
            self._remove_view_privileges(current_view)
            self._delete_view(current_view)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '删除失败！\n{e}'.format(e=str(e)))
        return get_response(RequestCode.SUCCESS, '删除成功！')

    def _update_view(self, view, args):
        log = DBOperationLog(
                    operation_type='修改', 
                    operator=g.current_user.username, 
                    target_type='View', 
                    target_name=view.name, \
                    target_id=int(view.id), 
                    target_detail=view.get_content_str(prefix="修改前：")
                    )
        db.session.add(log)
        view.name = args['name']
        view.acl = args['acl']
        db.session.add(view)
        view_list = db.session.query(DBView).all()
        view.make_view('modify', view_list)

    def _delete_view(self, view):
        log = DBOperationLog(
                    operation_type='删除', 
                    operator=g.current_user.username, 
                    target_type='View', 
                    target_name=view.name,
                    target_id=int(view.id), 
                    target_detail=view.get_content_str(prefix="修改前：")
                    )
        db.session.add(log)
        db.session.delete(view)
        view_list = db.session.query(DBView).all()
        view.make_view('delete', view_list)

    def _remove_view_privileges(self, current_view):
        """Remove all the privileges from the indicated view."""
        current_view_privileges_query = DBPrivilege.query.filter(
                    DBPrivilege.resource_id==current_view.id, 
                    DBPrivilege.resource_type==ResourceType.VIEW
                    )
        current_view_privileges = current_view_privileges_query.all()
        for view_privilege in current_view_privileges:
            DBRolePrivilege.query.filter(
                    DBRolePrivilege.privilege_id == view_privilege.id
                    ).delete()
        current_view_privileges_query.delete()

