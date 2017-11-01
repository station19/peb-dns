from flask_restful import Api, Resource, url_for, reqparse, abort
from flask import current_app, g

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord, DBDNSServer
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege, Operation
from peb_dns.common.decorators import token_required
from peb_dns import db
from peb_dns.common.util import ResourceContent
from sqlalchemy import and_, or_
from datetime import datetime


class ResourceAmount(Resource):

    method_decorators = [token_required]

    def get(self):
        return dict(server_amount=DBDNSServer.query.count(), view_amount=DBView.query.count(), zone_amount=DBZone.query.count(), record_amount=DBRecord.query.count())


class DNSServerResolveRate(Resource):

    method_decorators = [token_required]

    def post(self):
        pass


class DNSServerStatus(Resource):

    method_decorators = [token_required]

    def get(self):
        pass




