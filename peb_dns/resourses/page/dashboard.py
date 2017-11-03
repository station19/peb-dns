from flask_restful import Api, Resource, url_for, reqparse, abort
from flask import current_app, g, request

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord, DBDNSServer
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege, Operation
from peb_dns.common.decorators import token_required
from peb_dns import db
from peb_dns.common.util import ResourceContent, ZBapi
from sqlalchemy import and_, or_
from datetime import datetime

datetime.strftime


class ResourceAmount(Resource):

    method_decorators = [token_required]

    def get(self):
        return dict(server_amount=DBDNSServer.query.count(), view_amount=DBView.query.count(), zone_amount=DBZone.query.count(), record_amount=DBRecord.query.count())


class DNSServerResolveRate(Resource):

    method_decorators = [token_required]

    # def __init__(self):
    #     args = request.args
    #     super(DNSServerResolveRate, self).__init__()

    def get(self):
        args = request.args
        start_time = datetime.strptime(args['start_time'], "%Y-%m-%d-%H-%M") 
        end_time = datetime.now()
        if args.get('end_time'):
            end_time = datetime.strptime(args['end_time'], "%Y-%m-%d-%H-%M")
        dns_servers = DBDNSServer.query.all()
        resolve_rates = {}
        for dns_server in dns_servers:
            resolve_rate = dns_server.get_resolve_rate(start_time, end_time)
            resolve_rates[dns_server.host] = resolve_rate
        return resolve_rates


class DNSServerStatus(Resource):

    method_decorators = [token_required]

    # def __init__(self):
    #     self.get_reqparse = reqparse.RequestParser()
    #     self.get_reqparse.add_argument('server_id', type = int, location = 'json', required=True)
    #     super(DNSServerStatus, self).__init__()

    def get(self):
        args = request.args
        # args = self.get_reqparse.parse_args()
        current_server = DBDNSServer.query.get(int(args['server_id']))
        if not current_server:
            return dict(message='Failed', error="ID为 {e} 的server不存在！".format(e=args['server_id']))
        return current_server.get_server_status()



