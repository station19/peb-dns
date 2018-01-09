from flask_restful import Api, Resource, url_for, reqparse, abort, marshal_with, fields, marshal
from flask import current_app, g, request

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord, DBDNSServer
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.decorators import token_required, admin_required, permission_required, indicated_privilege_required, resource_exists_required
from peb_dns.common.util import getETCDclient, get_response, get_response_wrapper_fields
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING, ROLE_MAPPINGS, DefaultPrivilege
from peb_dns import db
from sqlalchemy import and_, or_
from datetime import datetime
from peb_dns.common.request_code import RequestCode


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

    def get(self):
        """Get record list."""
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
            server_query = server_query.filter(DBDNSServer.host.like('%'+host+'%'))
        if ip is not None:
            server_query = server_query.filter(DBDNSServer.ip.like('%'+ip+'%'))
        if env is not None:
            server_query = server_query.filter(DBDNSServer.env.like('%'+env+'%'))
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
        response_wrapper_fields = get_response_wrapper_fields(fields.Nested(paginated_server_fields))
        response_wrapper = get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)
        return marshal(response_wrapper, response_wrapper_fields)

    @indicated_privilege_required(DefaultPrivilege.SERVER_ADD)
    def post(self):
        """Create new server."""
        args = dns_server_common_parser.parse_args()
        unique_server = db.session.query(DBDNSServer).filter(
                or_(DBDNSServer.host==args['host'], DBDNSServer.ip==args['ip'])).all()
        if unique_server:
            return get_response(RequestCode.OTHER_FAILED,  '创建失败! 重复的Server，相同Host或IP地址已存在！')
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
        return get_response(RequestCode.SUCCESS, '创建成功！')

    def init_server(self):
        pass

    def _add_privilege_for_server(self, new_server):
        """Add privilege for the new server."""
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

    @resource_exists_required(ResourceType.SERVER)
    @permission_required(ResourceType.SERVER, Operation.ACCESS)
    def get(self, server_id):
        """Get the detail info of the single server."""
        current_server = DBDNSServer.query.get(server_id)
        results_wrapper = marshal(current_server, server_fields)
        return get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)

    @resource_exists_required(ResourceType.SERVER)
    @permission_required(ResourceType.SERVER, Operation.UPDATE)
    def put(self, server_id):
        """Update the indicated server."""
        current_server = DBDNSServer.query.get(server_id)
        args = dns_server_common_parser.parse_args()
        try:
            self._update_server(current_server, args)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '修改失败！')
        return get_response(RequestCode.SUCCESS, '修改成功！')

    @resource_exists_required(ResourceType.SERVER)
    @permission_required(ResourceType.SERVER, Operation.DELETE)
    def delete(self, server_id):
        """Delete the indicated server."""
        current_server = DBDNSServer.query.get(server_id)
        try:
            self._delete_server(current_server)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.SUCCESS, '删除失败！')
        return get_response(RequestCode.SUCCESS, '删除成功！')


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
        """Remove all the privileges from the indicated server."""
        current_record_privileges_query = DBPrivilege.query.filter(
                        DBPrivilege.resource_id==current_server.id, 
                        DBPrivilege.resource_type==ResourceType.SERVER
                        )
        current_record_privileges = current_record_privileges_query.all()
        for record_privilege in current_record_privileges:
            DBRolePrivilege.query.filter(
                        DBRolePrivilege.privilege_id == record_privilege.id
                        ).delete()
        current_record_privileges_query.delete()



class DNSBindConf(Resource):
    method_decorators = [admin_required, token_required] 

    def __init__(self):
        super(DNSBindConf, self).__init__()
        self.post_reqparse = reqparse.RequestParser()
        self.post_reqparse.add_argument('bind_conf', 
                                    type = str, 
                                    location = 'json', 
                                    required=True)

    def get(self):
        try:
            etcd_client = getETCDclient()
            bind_conf_content = etcd_client.read(
                current_app.config.get('BIND_CONF')).value
            return get_response(RequestCode.SUCCESS, '获取成功！', dict(bind_conf=bind_conf_content))
        except Exception as e:
            return get_response(RequestCode.OTHER_FAILED,  '获取数据失败！')
        
    def post(self):
        try:
            req = self.post_reqparse.parse_args()
            bind_conf_content = req.get('bind_conf')
            etcd_client = getETCDclient()
            etcd_client.write(
                current_app.config.get('BIND_CONF'), 
                bind_conf_content, 
                prevExist=True
                )
            time.sleep(0.5)
            return get_response(RequestCode.SUCCESS, '修改成功')
        except Exception as e:
            return get_response(RequestCode.OTHER_FAILED,  '提交数据失败 ！')


class DNSServerEnvs(Resource):
    method_decorators = [token_required] 

    def get(self):
        return current_app.config['SERVER_ENVS']

    