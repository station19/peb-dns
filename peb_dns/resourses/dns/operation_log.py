from flask_restful import Api, Resource, url_for, reqparse, abort, marshal_with, fields, marshal
from flask import current_app, g, request

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord
from peb_dns.common.decorators import token_required
from peb_dns import db
from sqlalchemy import and_, or_
from datetime import datetime


log_fields = {
    'id': fields.Integer,
    'operation_time': fields.String,
    'operation_type': fields.String,
    'operator': fields.String,
    'target_type': fields.String,
    'target_name': fields.String,
    'target_id': fields.String,
    'target_detail': fields.String,
}

paginated_log_fields = {
    'total': fields.Integer,
    'operation_logs': fields.List(fields.Nested(log_fields)),
    'current_page': fields.Integer
}

class DNSOperationLogList(Resource):

    method_decorators = [token_required] 

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(DNSOperationLogList, self).__init__()

    def get(self):
        args = request.args
        current_page = args.get('currentPage', 1, type=int)
        page_size = args.get('pageSize', 10, type=int)

        id = args.get('id', type=int)
        operation_type = args.get('operation_type', type=str)
        operator = args.get('operator', type=str)
        target_type = args.get('target_type', type=str)
        target_name = args.get('target_name', type=str)
        oplog_query = DBOperationLog.query
        if id:
            oplog_query = oplog_query.filter_by(id=id)
        if operation_type:
            oplog_query = oplog_query.filter_by(operation_type=operation_type)
        if operator:
            oplog_query = oplog_query.filter_by(operator=operator)
        if target_type:
            oplog_query = oplog_query.filter_by(target_type=target_type)
        if target_name:
            oplog_query = oplog_query.filter_by(target_name=target_name)


        marshal_records = marshal(oplog_query
                    .order_by(DBOperationLog.id.desc())
                    .paginate(current_page, page_size, error_out=False).items, log_fields)
        results_wrapper = {'total': oplog_query.count(), 
                           'operation_logs': marshal_records, 
                           'current_page': current_page}
        return marshal(results_wrapper, paginated_log_fields)


class DNSOperationLog(Resource):

    method_decorators = [token_required] 

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(DNSOperationLog, self).__init__()

    def get(self, log_id):
        current_log = DBOperationLog.query.get(log_id)
        return { 'message' : "aaaaaaaaaaaaaa" }, 200

