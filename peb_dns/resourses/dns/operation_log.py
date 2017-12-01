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
        """Get zone list."""
        args = request.args
        current_page = args.get('currentPage', 1, type=int)
        page_size = args.get('pageSize', 10, type=int)

        id = args.get('id', type=int)
        operation_type = args.get('operation_type', type=str)
        operator = args.get('operator', type=str)
        target_type = args.get('target_type', type=str)
        target_name = args.get('target_name', type=str)
        oplog_query = DBOperationLog.query
        if id is not None:
            oplog_query = oplog_query.filter(DBOperationLog.id==id)
        if operation_type is not None:
            oplog_query = oplog_query.filter(DBOperationLog.operation_type==operation_type)
        if operator is not None:
            oplog_query = oplog_query.filter(DBOperationLog.operator==operator)
        if target_type is not None:
            oplog_query = oplog_query.filter(DBOperationLog.target_type==target_type)
        if target_name is not None:
            oplog_query = oplog_query.filter(DBOperationLog.target_name==target_name) 
        marshal_records = marshal(
                    oplog_query.order_by(DBOperationLog.id.desc()).paginate(
                        current_page, 
                        page_size, 
                        error_out=False).items, log_fields
                    )
        results_wrapper = {
            'total': oplog_query.count(), 
            'operation_logs': marshal_records, 
            'current_page': current_page
            }
        response_wrapper_fields = get_response_wrapper_fields(fields.Nested(paginated_log_fields))
        response_wrapper = get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)
        return marshal(response_wrapper, response_wrapper_fields)


class DNSOperationLog(Resource):
    method_decorators = [token_required] 

    def get(self, log_id):
        """Get the detail info of the single log."""
        current_log = DBOperationLog.query.get(log_id)
        if not current_log:
            return get_response(RequestCode.OTHER_FAILED,  "当前记录 {} 不存在！".format(str(log_id)))
        results_wrapper = marshal(current_log, log_fields)
        return get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)

