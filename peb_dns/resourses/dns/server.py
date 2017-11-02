from flask_restful import Api, Resource, url_for, reqparse, abort, marshal_with, fields
from flask import current_app, g

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord, DBDNSServer
from peb_dns.models.account import Operation, ResourceType, DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.decorators import token_required
from peb_dns import db
from peb_dns.common.util import ResourceContent
from sqlalchemy import and_, or_
from datetime import datetime


dns_server_common_parser = reqparse.RequestParser()
dns_server_common_parser.add_argument('host', type = str, location = 'json', required=True, help='host')
dns_server_common_parser.add_argument('ip', type = str, location = 'json', required=True)
dns_server_common_parser.add_argument('env', type = str, location = 'json', required=True)
dns_server_common_parser.add_argument('dns_server_type', type = str, location = 'json', required=True)
dns_server_common_parser.add_argument('zb_process_itemid', type = str, location = 'json', required=True)
dns_server_common_parser.add_argument('zb_port_itemid', type = str, location = 'json', required=True)
dns_server_common_parser.add_argument('zb_resolve_itemid', type = str, location = 'json', required=True)
dns_server_common_parser.add_argument('zb_resolve_rate_itemid', type = str, location = 'json', required=True)

server_fields = {
    'host': fields.String,
    'ip': fields.String,
    'env': fields.String,
    'dns_server_type': fields.String,
    'zb_process_itemid': fields.String,
    'zb_port_itemid': fields.String,
    'zb_resolve_itemid': fields.String,
    'zb_resolve_rate_itemid': fields.String,
}

class DNSServerList(Resource):

    method_decorators = [token_required]

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(DNSServerList, self).__init__()

    @marshal_with(server_fields, envelope='servers')
    def get(self):
        return DBDNSServer.query.all()

    def post(self):
        args = dns_server_common_parser.parse_args()

        unique_server = db.session.query(DBDNSServer).filter(or_(DBDNSServer.host==args['host'], DBDNSServer.ip==args['ip'])).all()
        if unique_server:
            return dict(message='Failed', error='创建失败! 重复的Server，相同Host或IP地址已存在！')

        new_server = DBDNSServer(**args)
        db.session.add(new_server)
        db.session.flush()
        self._add_privilege_for_server(new_server)
        log = DBOperationLog(operation_type='添加', operator=g.current_user.username, target_type='DNSServer', target_name=new_server.host, \
                target_id=int(new_server.id), target_detail=ResourceContent.getServerContent(new_server))
        db.session.add(log)
        db.session.commit()

        # app_object = current_app._get_current_object()
        # init_cmd = current_app.config['SERVER_INIT_CMD']
        # init_server_thread = threading.Thread(target=initServer, args=(init_cmd, app_object, new_server.id))
        # init_server_thread.start()
        
        return dict(message='OK'), 201

    def init_server(self):
        pass

    def _add_privilege_for_server(self, new_server):
        access_privilege_name = new_server.host + '#' + str(Operation.ACCESS)
        update_privilege_name = new_server.host + '#' + str(Operation.UPDATE)
        delete_privilege_name = new_server.host + '#' + str(Operation.DELETE)
        access_privilege = DBPrivilege(name=access_privilege_name, resource_type=ResourceType.SERVER, operation=Operation.ACCESS, resource_id=new_server.id)
        update_privilege = DBPrivilege(name=update_privilege_name, resource_type=ResourceType.SERVER, operation=Operation.UPDATE, resource_id=new_server.id)
        delete_privilege = DBPrivilege(name=delete_privilege_name, resource_type=ResourceType.SERVER, operation=Operation.DELETE, resource_id=new_server.id)
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


class DNSServer(Resource):

    method_decorators = [token_required]

    def get(self, server_id):
        current_server = DBDNSServer.query.get(server_id)
        args = dns_server_common_parser.parse_args()

        return { 'message' : "哈哈哈哈哈哈" }, 200

    def put(self, server_id):
        current_server = DBDNSServer.query.get(server_id)
        args = dns_server_common_parser.parse_args()
        try:
            self._update_server(current_server, args)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200


    def delete(self, server_id):
        current_server = DBDNSServer.query.get(server_id)
        try:
            self._delete_server(current_server)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200


    def _update_server(self, server, args):
        try:
            log = DBOperationLog(operation_type='修改', operator=g.current_user.username, target_type='Server', target_name=server.host, \
                    target_id=int(server.id), target_detail=ResourceContent.getServerContent(server, prefix="修改前："))
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
        except Exception as e:
            raise e

    def _delete_server(self, server):
        try:
            log = DBOperationLog(operation_type='删除', operator=g.current_user.username, target_type='Server', target_name=server.host, \
                    target_id=int(server.id), target_detail=ResourceContent.getServerContent(server))
            db.session.add(log)
            self._remove_server_privileges(server)
            db.session.delete(server)
        except Exception as e:
            raise e

    def _remove_server_privileges(self, current_server):
        current_record_privileges_query = DBPrivilege.query.filter(DBPrivilege.resource_id==current_server.id, DBPrivilege.resource_type==ResourceType.SERVER)
        current_record_privileges = current_record_privileges_query.all()
        for record_privilege in current_record_privileges:
            DBRolePrivilege.query.filter(DBRolePrivilege.privilege_id == record_privilege.id).delete()
        current_record_privileges_query.delete()


