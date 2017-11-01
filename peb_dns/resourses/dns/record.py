from flask_restful import Api, Resource, url_for, reqparse, abort
from flask import current_app, g

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord
from peb_dns.models.account import Operation, ResourceType, DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.decorators import token_required
from peb_dns import db
from peb_dns.common.util import ResourceContent
from sqlalchemy import and_, or_
from datetime import datetime


dns_record_common_parser = reqparse.RequestParser()
dns_record_common_parser.add_argument('host', type = str, location = 'json', required=True, help='host name')
dns_record_common_parser.add_argument('record_type', type = str, location = 'json', required=True, help='record type')
dns_record_common_parser.add_argument('ttl', type = str, location = 'json', required=True, help='ttl')
dns_record_common_parser.add_argument('value', type = str, location = 'json', required=True, help='value')
dns_record_common_parser.add_argument('view_name', type = str, location = 'json', required=True, help='view_name')
dns_record_common_parser.add_argument('comment', type = str, location = 'json', required=True, help='comment')
dns_record_common_parser.add_argument('zone_id', type = int, location = 'json', required=True, help='zone id')


class DNSRecordList(Resource):

    method_decorators = [token_required] 

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(DNSRecordList, self).__init__()

    def get(self):
        DBZone.query.all()
        return { 'message' : "aaaaaaaaaaaaaa" }, 200

    def post(self):
        args = dns_record_common_parser.parse_args()
        current_zone = DBZone.query.get(args['zone_id'])
        if not current_zone:
            return dict(message='Failed', error_msg='创建失败！当前Zone不存在，请检查zone_id是否正确！')
        unique_record = DBRecord.query.filter_by(zone_id=args['zone_id'], host=args['host'], view_name=args['view_name']).first()
        if unique_record:
            return dict(message='Failed', error_msg='创建失败 !重复的记录！！同样的Zone，同样的主机，同样的View 的记录只能存在一个。')
        args['creator'] = g.current_user.username
        new_record = DBRecord(**args)
        db.session.add(new_record)
        db.session.flush()
        log = DBOperationLog(operation_type='添加', operator=args['creator'], target_type='Record', target_name=new_record.host, \
                target_id=int(new_record.id), target_detail=ResourceContent.getRecordContent(new_record))
        db.session.add(log)
        try:
            record_list = db.session.query(DBRecord).filter(DBRecord.zone_id == args['zone_id'], DBRecord.view_name == args['view_name'], DBRecord.host != '@').all()
            new_record.make_record(current_zone.name, record_list)
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e)))

        self._add_privilege_for_record(current_zone, new_record)
        db.session.commit()

        return dict(message='OK'), 201


    def _add_privilege_for_record(self, current_zone, new_record):
        access_privilege_name = new_record.view_name + '#' + current_zone.name + '#' + new_record.host + '#' + str(Operation.ACCESS)
        update_privilege_name = new_record.view_name + '#' + current_zone.name + '#' + new_record.host + '#' + str(Operation.UPDATE)
        delete_privilege_name = new_record.view_name + '#' + current_zone.name + '#' + new_record.host + '#' + str(Operation.DELETE)
        access_privilege = DBPrivilege(name=access_privilege_name, resource_type=ResourceType.RECORD, operation=Operation.ACCESS, resource_id=new_record.id)
        update_privilege = DBPrivilege(name=update_privilege_name, resource_type=ResourceType.RECORD, operation=Operation.UPDATE, resource_id=new_record.id)
        delete_privilege = DBPrivilege(name=delete_privilege_name, resource_type=ResourceType.RECORD, operation=Operation.DELETE, resource_id=new_record.id)
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



class DNSRecord(Resource):

    method_decorators = [token_required]

    def get(self, record_id):
        args = dns_record_common_parser.parse_args()
        current_record = DBRecord.query.get(record_id)
        if not current_record:
            abort(404, message="当前记录 {} 不存在！".format(str(record_id)))
        return { 'message' : "哈哈哈哈哈哈" }, 200

    def put(self, record_id):
        args = dns_record_common_parser.parse_args()
        current_record = DBRecord.query.get(record_id)
        if not current_record:
            abort(404, message="当前记录 {} 不存在！".format(str(record_id)))
        current_zone = DBZone.query.get(current_record.zone_id)
        unique_record = DBRecord.query.filter_by(zone_id=args['zone_id'], host=args['host'], view_name=args['view_name']).first()
        if unique_record:
            return dict(message='Failed', error_msg='修改失败 !重复的记录！！同样的Zone，同样的主机，同样的View 的记录只能存在一个。')
        try:
            self._update_record(current_zone, current_record, args)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200

    def delete(self, record_id):
        current_record = DBRecord.query.get(record_id)
        if not current_record:
            abort(404, message="当前记录 {} 不存在！".format(str(record_id)))
        current_zone = DBZone.query.get(current_record.zone_id)
        try:
            self._delete_record(current_zone, current_record)
            self._remove_record_privileges(current_zone, current_record)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200

    def _update_record(self, current_zone, current_record, args):
        current_record.host = args['host']
        current_record.record_type = args['record_type']
        current_record.ttl = args['ttl']
        current_record.value = args['value']
        current_record.view_name = args['view_name']
        current_record.comment = args['comment']
        current_record.zone_id = args['zone_id']
        current_record.gmt_modified = datetime.now()
        db.session.add(current_record)
        log = DBOperationLog(operation_type='修改', operator=g.current_user.username, target_type='Record', target_name=current_record.host, \
                target_id=int(current_record.id), target_detail=ResourceContent.getRecordContent(current_record))
        db.session.add(log)
        record_list = db.session.query(DBRecord).filter(DBRecord.zone_id == args['zone_id'], DBRecord.view_name == args['view_name'], DBRecord.host != '@').all()
        current_record.make_record(current_zone.name, record_list)


    def _delete_record(self, current_zone, current_record):
        log = DBOperationLog(operation_type='删除', operator=g.current_user.username, target_type='Record', target_name=current_record.host, \
                target_id=int(current_record.id), target_detail=ResourceContent.getRecordContent(current_record))
        db.session.add(log)
        db.session.delete(current_record)
        record_list = db.session.query(DBRecord).filter(DBRecord.zone_id == current_record.zone_id, DBRecord.view_name == current_record.view_name, DBRecord.host != '@').all()
        current_record.make_record(current_zone.name, record_list)


    def _remove_record_privileges(self, current_zone, current_record):
        current_record_privileges_query = DBPrivilege.query.filter(DBPrivilege.resource_id==current_record.id, DBPrivilege.resource_type==ResourceType.RECORD)
        current_record_privileges = current_record_privileges_query.all()
        for record_privilege in current_record_privileges:
            DBRolePrivilege.query.filter(DBRolePrivilege.privilege_id == record_privilege.id).delete()
        current_record_privileges_query.delete()
        


        

