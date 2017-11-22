from flask_restful import Api, Resource, url_for, reqparse, abort, marshal_with, fields, marshal
from flask import current_app, g, request

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord, DBDNSServer
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING
from peb_dns.common.decorators import token_required
from peb_dns import db
from sqlalchemy import and_, or_
from datetime import datetime


dns_server_common_parser = reqparse.RequestParser()
dns_server_common_parser.add_argument('host', 
                                    type = str, 
                                    location = 'json', 
                                    required=True, 
                                    help='host')
dns_server_common_parser.add_argument('ip', 
                                    type = str, 
                                    location = 'json', 
                                    required=True)
dns_server_common_parser.add_argument('env', 
                                    type = str, 
                                    location = 'json', 
                                    required=True)
dns_server_common_parser.add_argument('dns_server_type', 
                                    type = str, 
                                    location = 'json', 
                                    required=True)
dns_server_common_parser.add_argument('zb_process_itemid', 
                                    type = str, 
                                    location = 'json', 
                                    required=True)
dns_server_common_parser.add_argument('zb_port_itemid', 
                                    type = str, 
                                    location = 'json', 
                                    required=True)
dns_server_common_parser.add_argument('zb_resolve_itemid', 
                                    type = str, 
                                    location = 'json', 
                                    required=True)
dns_server_common_parser.add_argument('zb_resolve_rate_itemid', 
                                    type = str, 
                                    location = 'json', 
                                    required=True)

server_fields = {
    'id':fields.Integer,
    'host': fields.String,
    'ip': fields.String,
    'env': fields.String,
    'dns_server_type': fields.String,
    'zb_process_itemid': fields.String,
    'zb_port_itemid': fields.String,
    'zb_resolve_itemid': fields.String,
    'zb_resolve_rate_itemid': fields.String,
    'can_update': fields.Boolean,
    'can_delete': fields.Boolean
}

paginated_server_fields = {
    'total': fields.Integer,
    'servers': fields.List(fields.Nested(server_fields)),
    'current_page': fields.Integer
}

class DNSServerList(Resource):
    method_decorators = [token_required]

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(DNSServerList, self).__init__()

    def get(self):
        args = request.args
        current_page = request.args.get('currentPage', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)

        id = args.get('id', type=int)
        host = args.get('host', type=str)
        ip = args.get('ip', type=str)
        env = args.get('env', type=str)
        dns_server_type = args.get('dns_server_type', type=str)
        server_query = db.session.query(DBDNSServer) \
            .join(DBPrivilege, and_(
                DBDNSServer.id == DBPrivilege.resource_id, 
                DBPrivilege.resource_type == ResourceType.SERVER, 
                DBPrivilege.operation == Operation.ACCESS
                )) \
            .join(DBRolePrivilege, and_(
                DBPrivilege.id == DBRolePrivilege.privilege_id
                )) \
            .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
            .join(DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
            .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
            .filter(DBUser.id == g.current_user.id)
        if id is not None:
            server_query = server_query.filter(DBDNSServer.id==id)
        if host is not None:
            server_query = server_query.filter(DBDNSServer.host==host)
        if ip is not None:
            server_query = server_query.filter(DBDNSServer.ip==ip)
        if env is not None:
            server_query = server_query.filter(DBDNSServer.env==env)
        if dns_server_type is not None:
            server_query = server_query.filter(DBDNSServer.dns_server_type==dns_server_type)
        marshal_records = marshal(
                server_query.order_by(DBDNSServer.id.desc()).paginate(
                    current_page, 
                    page_size, 
                    error_out=False
                ).items, server_fields)
        results_wrapper = {
            'total': server_query.count(), 
            'servers': marshal_records, 
            'current_page': current_page
            }
        return marshal(results_wrapper, paginated_server_fields)

    def post(self):
        if not g.current_user.can_add_server:
            return dict(message='Failed', 
                error='无权限！您无权限添加Server，请联系管理员。'), 403
        args = dns_server_common_parser.parse_args()
        unique_server = db.session.query(DBDNSServer).filter(
                or_(DBDNSServer.host==args['host'], DBDNSServer.ip==args['ip'])).all()
        if unique_server:
            return dict(message='Failed', 
                error='创建失败! 重复的Server，相同Host或IP地址已存在！'), 400
        new_server = DBDNSServer(**args)
        db.session.add(new_server)
        db.session.flush()
        self._add_privilege_for_server(new_server)
        log = DBOperationLog(
                operation_type='添加', 
                operator=g.current_user.username, 
                target_type='Server', 
                target_name=new_server.host,
                target_id=int(new_server.id), 
                target_detail=new_server.get_content_str())
        db.session.add(log)
        db.session.commit()
        return dict(message='OK'), 201

    def init_server(self):
        pass

    def _add_privilege_for_server(self, new_server):
        access_privilege_name = 'SERVER#' + new_server.host + \
                '#' + OPERATION_STR_MAPPING[Operation.ACCESS]
        update_privilege_name = 'SERVER#' + new_server.host + \
                '#' + OPERATION_STR_MAPPING[Operation.UPDATE]
        delete_privilege_name = 'SERVER#' + new_server.host + \
                '#' + OPERATION_STR_MAPPING[Operation.DELETE]
        access_privilege = DBPrivilege(
                name=access_privilege_name, 
                resource_type=ResourceType.SERVER, 
                operation=Operation.ACCESS, 
                resource_id=new_server.id
                )
        update_privilege = DBPrivilege(
                name=update_privilege_name, 
                resource_type=ResourceType.SERVER, 
                operation=Operation.UPDATE, 
                resource_id=new_server.id
                )
        delete_privilege = DBPrivilege(
                name=delete_privilege_name, 
                resource_type=ResourceType.SERVER, 
                operation=Operation.DELETE, 
                resource_id=new_server.id
                )
        db.session.add(access_privilege)
        db.session.add(update_privilege)
        db.session.add(delete_privilege)
        db.session.flush()
        for role in ['admin', 'server_admin', 'server_guest']:
            role_access =  DBRolePrivilege(
                                role_id=ROLE_MAPPINGS[role],
                                privilege_id=access_privilege.id)
            db.session.add(role_access)
            if role not in ['server_guest']:
                role_update =  DBRolePrivilege(
                                    role_id=ROLE_MAPPINGS[role],
                                    privilege_id=update_privilege.id)
                role_delete =  DBRolePrivilege(
                                    role_id=ROLE_MAPPINGS[role],
                                    privilege_id=delete_privilege.id)
                db.session.add(role_update)
                db.session.add(role_delete)


class DNSServer(Resource):
    method_decorators = [token_required]

    @marshal_with(server_fields)
    def get(self, server_id):
        current_server = DBDNSServer.query.get(server_id)
        if not current_server:
            abort(404)
        if not g.current_user.can_do(
                        Operation.ACCESS, 
                        ResourceType.SERVER, 
                        current_server.id):
            return dict(message='Failed', 
                error='无权限！您无权访问当前Server，请联系管理员。'), 403
        return current_server


    def put(self, server_id):
        current_server = DBDNSServer.query.get(server_id)
        if not current_server:
            abort(404)
        if not g.current_user.can_do(
                        Operation.UPDATE, 
                        ResourceType.SERVER, 
                        current_server.id):
            return dict(message='Failed', 
                error='无权限！您无权修改当前Server，请联系管理员。'), 403
        args = dns_server_common_parser.parse_args()
        try:
            self._update_server(current_server, args)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 400
        return dict(message='OK'), 200

    def delete(self, server_id):
        current_server = DBDNSServer.query.get(server_id)
        if not current_server:
            abort(404)
        if not g.current_user.can_do(
                        Operation.DELETE, 
                        ResourceType.SERVER, 
                        current_server.id):
            return dict(message='Failed', 
                error='无权限！您无权删除当前Server，请联系管理员。'), 403
        try:
            self._delete_server(current_server)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', 
                error="{e}".format(e=str(e))), 400
        return dict(message='OK'), 200


    def _update_server(self, server, args):
        log = DBOperationLog(
                operation_type='修改', 
                operator=g.current_user.username, 
                target_type='Server', 
                target_name=server.host,
                target_id=int(server.id), 
                target_detail=server.get_content_str(prefix="修改前："))
        db.session.add(log)
        server.host = args['host']
        server.ip = args['ip']
        server.env = args['env']
        server.dns_server_type = args['dns_server_type']
        server.zb_process_itemid = args['zb_process_itemid']
        server.zb_port_itemid = args['zb_port_itemid']
        server.zb_resolve_itemid = args['zb_resolve_itemid']
        server.zb_resolve_rate_itemid = args['zb_resolve_rate_itemid']
        db.session.add(server)

    def _delete_server(self, server):
        log = DBOperationLog(
                operation_type='删除', 
                operator=g.current_user.username, 
                target_type='Server', 
                target_name=server.host,
                target_id=int(server.id), 
                target_detail=server.get_content_str())
        db.session.add(log)
        self._remove_server_privileges(server)
        db.session.delete(server)

    def _remove_server_privileges(self, current_server):
        current_record_privileges_query = DBPrivilege.query.filter(
                        DBPrivilege.resource_id==current_server.id, 
                        DBPrivilege.resource_type==ResourceType.SERVER)
        current_record_privileges = current_record_privileges_query.all()
        for record_privilege in current_record_privileges:
            DBRolePrivilege.query.filter(
                        DBRolePrivilege.privilege_id == record_privilege.id
                        ).delete()
        current_record_privileges_query.delete()


