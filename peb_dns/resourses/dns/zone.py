from flask_restful import Api, Resource, url_for, reqparse, abort, marshal_with, fields, marshal
from flask import current_app, g, request

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING
from peb_dns.common.decorators import token_required
from peb_dns.common.util import ZONE_GROUP_MAPPING
from peb_dns import db
from sqlalchemy import and_, or_
from datetime import datetime


dns_zone_common_parser = reqparse.RequestParser()
dns_zone_common_parser.add_argument('name', 
                                    type = str, 
                                    location = 'json', 
                                    required=True, 
                                    help='zone name.')
dns_zone_common_parser.add_argument('zone_group', 
                                    type = int, 
                                    location = 'json', 
                                    required=True)
dns_zone_common_parser.add_argument('zone_type', 
                                    type = str, 
                                    location = 'json')
dns_zone_common_parser.add_argument('forwarders', 
                                    type = str, 
                                    location = 'json')
dns_zone_common_parser.add_argument('view_ids', 
                                    type = int, 
                                    location = 'json', 
                                    action='append')

zone_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'zone_group': fields.Integer,
    'zone_type': fields.String,
    'forwarders': fields.String,
    'view_name_list': fields.String,
    'can_update': fields.Boolean,
    'can_delete': fields.Boolean,
    'view_ids':fields.List(fields.Integer)
}

paginated_zone_fields = {
    'total': fields.Integer,
    'zones': fields.List(fields.Nested(zone_fields)),
    'current_page': fields.Integer
}

class DNSZoneList(Resource):
    method_decorators = [token_required] 

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(DNSZoneList, self).__init__()

    def get(self):
        args = request.args
        current_page = request.args.get('currentPage', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)
        id = args.get('id', type=int)
        name = args.get('name', type=str)
        zone_group = args.get('zone_group', type=int)
        zone_type = args.get('zone_type', type=str)
        zone_query = DBZone.query \
            .join(DBPrivilege, and_(
                DBZone.id == DBPrivilege.resource_id, 
                DBPrivilege.resource_type == ResourceType.ZONE, 
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
            zone_query = zone_query.filter(DBZone.id==id)
        if name is not None:
            zone_query = zone_query.filter(DBZone.name==name)
        if zone_group is not None:
            zone_query = zone_query.filter(DBZone.zone_group==zone_group)
        if zone_type is not None:
            zone_query = zone_query.filter(DBZone.zone_type==zone_type)
        marshal_records = marshal(
                zone_query.order_by(DBZone.id.desc()).paginate(
                    current_page, 
                    page_size, 
                    error_out=False).items, zone_fields)
        results_wrapper = {
                    'total': zone_query.count(), 
                    'zones': marshal_records, 
                    'current_page': current_page
                    }
        return marshal(results_wrapper, paginated_zone_fields)

    def post(self):
        if not g.current_user.can_add_zone:
            return dict(message='Failed', 
                error='无权限！您无权限添加Zone，请联系管理员。'), 403
        args = dns_zone_common_parser.parse_args()
        zone_group = args['zone_group']
        if zone_group in (1, 2):
            view_ids = args['view_ids']
            unique_zone = db.session.query(DBZone).filter(
                        and_(DBZone.name==args['name'].strip(), 
                        DBZone.zone_group.in_((1,2)))).first()
            if unique_zone:
                return dict(message='Failed', 
                        error_msg='创建失败！重复的Zone！！相同名字的Zone，\
                            每种类型域名下只能存在一个！'), 400
            if args['zone_type'] == 'forward only':
                args['forwarders'] = '; '.join(
                        [ip.strip() for ip in args['forwarders'].strip().split()]) + ';'
            new_zone = DBZone(**args)
            db.session.add(new_zone)
            db.session.flush()
            for view_id in view_ids:
                v = DBViewZone(
                        view_id=int(view_id),
                        zone_id=new_zone.id
                        )
                db.session.add(v)
            del args['view_ids']
        elif zone_group == 0:
            new_zone = DBZone(name=args['name'], zone_group=zone_group)
            db.session.add(new_zone)
            db.session.flush()
        log = DBOperationLog(
                    operation_type='添加', 
                    operator=g.current_user.username, 
                    target_type='Zone', 
                    target_name=new_zone.name, \
                    target_id=int(new_zone.id), 
                    target_detail=new_zone.get_content_str()
                    )
        db.session.add(log)
        try:
            new_zone.create()
            self._add_privilege_for_zone(new_zone)
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 400
        db.session.commit()
        return dict(message='OK'), 201


    def _add_privilege_for_zone(self, new_zone):
        access_privilege_name =  'ZONE#' + new_zone.name + \
                        '#' + OPERATION_STR_MAPPING[Operation.ACCESS]
        update_privilege_name =  'ZONE#' + new_zone.name + \
                        '#' + OPERATION_STR_MAPPING[Operation.UPDATE]
        delete_privilege_name =  'ZONE#' + new_zone.name + \
                        '#' + OPERATION_STR_MAPPING[Operation.DELETE]
        access_privilege = DBPrivilege(
                            name=access_privilege_name, 
                            resource_type=ResourceType.ZONE, 
                            operation=Operation.ACCESS, 
                            resource_id=new_zone.id
                            )
        update_privilege = DBPrivilege(
                            name=update_privilege_name, 
                            resource_type=ResourceType.ZONE, 
                            operation=Operation.UPDATE, 
                            resource_id=new_zone.id
                            )
        delete_privilege = DBPrivilege(
                            name=delete_privilege_name, 
                            resource_type=ResourceType.ZONE, 
                            operation=Operation.DELETE, 
                            resource_id=new_zone.id
                            )
        db.session.add(access_privilege)
        db.session.add(update_privilege)
        db.session.add(delete_privilege)
        db.session.flush()
        admin_access =  DBRolePrivilege(role_id=1, 
                            privilege_id=access_privilege.id)
        admin_update =  DBRolePrivilege(role_id=1, 
                            privilege_id=update_privilege.id)
        admin_delete =  DBRolePrivilege(role_id=1, 
                            privilege_id=delete_privilege.id)
        db.session.add(admin_access)
        db.session.add(admin_update)
        db.session.add(admin_delete)


class DNSZone(Resource):
    method_decorators = [token_required]

    @marshal_with(zone_fields)
    def get(self, zone_id):
        current_zone = DBZone.query.get(zone_id)
        if not current_zone:
            abort(404)
        if not g.current_user.can_do(
                        Operation.ACCESS, 
                        ResourceType.ZONE, 
                        current_zone.id):
            return dict(message='Failed', 
                    error='无权限！您无权限访问当前Zone，请联系管理员。'), 403
        return current_zone
        

    def put(self, zone_id):
        current_zone = DBZone.query.get(zone_id)
        if not current_zone:
            abort(404)
        if not g.current_user.can_do(
                        Operation.UPDATE, 
                        ResourceType.ZONE, 
                        current_zone.id):
            return dict(message='Failed', 
                    error='无权限！您无权限修改当前Zone，请联系管理员。'), 403
        args = dns_zone_common_parser.parse_args()
        try:
            self._update_zone(current_zone, args)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', 
                    error="{e}".format(e=str(e))), 400
        return dict(message='OK'), 200

    def delete(self, zone_id):
        current_zone = DBZone.query.get(zone_id)
        if not current_zone:
            abort(404)
        if not g.current_user.can_do(
                        Operation.UPDATE, 
                        ResourceType.ZONE, 
                        current_zone.id):
            return dict(message='Failed', 
                    error='无权限！您无权删除当前Zone，请联系管理员。'), 403
        try:
            self._remove_zone_privileges(current_zone)
            self._delete_zone(current_zone)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', 
                    error="{e}".format(e=str(e))), 400
        return dict(message='OK'), 200

    def _update_zone(self, current_zone, args):
        pre_views = current_zone.view_name_list
        log = DBOperationLog(
                    operation_type='修改', 
                    operator=g.current_user.username, 
                    target_type='Zone', 
                    target_name=current_zone.name,
                    target_id=int(current_zone.id), 
                    target_detail=current_zone.get_content_str(prefix="修改前：")
                    )
        db.session.add(log)
        if args['zone_type'] == 'forward only':
            current_zone.forwarders = '; '.join(
                    [ip.strip() for ip in args['forwarders'].strip().split()]) \
                    + ';'
        current_zone.name = args['name']
        current_zone.zone_group = args['zone_group']
        current_zone.zone_type = args['zone_type']
        # current_zone.forwarders = args['forwarders']
        db.session.add(current_zone)

        current_view_zones = DBViewZone.query.filter(
                    DBViewZone.zone_id==current_zone.id).all()
        for cvz in current_view_zones:
            db.session.delete(cvz)
        for view_id in args['view_ids']:
            vz = DBViewZone(zone_id=current_zone.id, view_id=int(view_id))
            db.session.add(vz)
        db.session.flush()
        current_zone.modify(pre_views)


    def _delete_zone(self, current_zone):
        log = DBOperationLog(
                    operation_type='删除', 
                    operator=g.current_user.username, 
                    target_type='Zone', 
                    target_name=current_zone.name,
                    target_id=int(current_zone.id), 
                    target_detail=current_zone.get_content_str(prefix="修改前：")
                    )
        db.session.add(log)

        DBViewZone.query.filter(DBViewZone.zone_id==current_zone.id).delete()
        DBRecord.query.filter(DBRecord.zone_id == current_zone.id).delete()
        db.session.delete(current_zone)
        current_zone.delete()


    def _remove_zone_privileges(self, current_zone):
        current_zone_records = DBRecord.query.filter(
                    DBRecord.zone_id == current_zone.id).all()
        for current_zone_record in current_zone_records:
            self._remove_record_privileges(current_zone, current_zone_record)
        current_zone_privileges_query = DBPrivilege.query.filter(
                    DBPrivilege.resource_id==current_zone.id, 
                    DBPrivilege.resource_type==ResourceType.ZONE
                    )
        current_zone_privileges = current_zone_privileges_query.all()
        for zone_privilege in current_zone_privileges:
            DBRolePrivilege.query.filter(
                    DBRolePrivilege.privilege_id == zone_privilege.id
                    ).delete()
        current_zone_privileges_query.delete()


    def _remove_record_privileges(self, current_zone, current_record):
        current_record_privileges_query = DBPrivilege.query.filter(
                    DBPrivilege.resource_id==current_record.id, 
                    DBPrivilege.resource_type==ResourceType.RECORD
                    )
        current_record_privileges = current_record_privileges_query.all()
        for record_privilege in current_record_privileges:
            DBRolePrivilege.query.filter(
                    DBRolePrivilege.privilege_id == record_privilege.id
                    ).delete()
        current_record_privileges_query.delete()



