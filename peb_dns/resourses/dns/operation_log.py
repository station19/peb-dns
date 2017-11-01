from flask_restful import Api, Resource, url_for, reqparse, abort
from flask import current_app, g

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord
from peb_dns.common.decorators import token_required
from peb_dns import db
from peb_dns.common.util import ResourceContent
from sqlalchemy import and_, or_
from datetime import datetime


class DNSOperationLogList(Resource):

    method_decorators = [token_required] 

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(DNSOperationLogList, self).__init__()

    def get(self):
        DBOperationLog.query.all()
        return { 'message' : "aaaaaaaaaaaaaa" }, 200



class DNSOperationLog(Resource):

    method_decorators = [token_required] 

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(DNSOperationLog, self).__init__()

    def get(self, log_id):
        current_log = DBOperationLog.query.get(log_id)
        return { 'message' : "aaaaaaaaaaaaaa" }, 200

