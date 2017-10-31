from flask_restful import Api, Resource, url_for, reqparse, abort
from flask import current_app, g

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog
from peb_dns.common.decorators import token_required
from peb_dns import db
from peb_dns.common.util import ResourceContent
from sqlalchemy import and_, or_
from datetime import datetime


dns_zone_common_parser = reqparse.RequestParser()
dns_zone_common_parser.add_argument('name', type = str, location = 'json', required=True, help='zone name.')
dns_zone_common_parser.add_argument('zone_group', type = int, location = 'json', required=True)
dns_zone_common_parser.add_argument('zone_type', type = str, location = 'json', required=True)
dns_zone_common_parser.add_argument('forwarders', type = str, location = 'json', required=True)
dns_zone_common_parser.add_argument('view_ids', type = int, location = 'json', action='append', required=True)



class DNSZoneList(Resource):

    method_decorators = [token_required] 

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(DNSZoneList, self).__init__()

    def get(self):
        DBZone.query.all()
        return { 'message' : "aaaaaaaaaaaaaa" }, 200

    def post(self):
        args = dns_zone_common_parser.parse_args()
        view_ids = args['view_ids']
        unique_zone = db.session.query(DBZone).filter(and_(DBZone.name==args['name'].strip(), DBZone.zone_group.in_((1,2)))).first()
        if unique_zone:
            return dict(message='Failed', error_msg='创建失败！重复的Zone！！相同名字的Zone，每种类型域名下只能存在一个！')
        if args['zone_type'] == 'forward only':
            args['forwarders'] = '; '.join([ip.strip() for ip in args['forwarders'].strip().split()]) + ';'
        # print(args)
        del args['view_ids']
        new_zone = DBZone(**args)
        db.session.add(new_zone)
        db.session.flush()
        log = DBOperationLog(operation_type='添加', operator=g.current_user.username, target_type='Zone', target_name=new_zone.name, \
                target_id=int(new_zone.id), target_detail=ResourceContent.getZoneContent(new_zone))
        db.session.add(log)
        for view_id in view_ids:
            v = DBViewZone(view_id=int(view_id), zone_id=new_zone.id)
            db.session.add(v)
        try:
            new_zone.create()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e)))
        db.session.commit()
        return dict(message='OK'), 201


class DNSZone(Resource):

    method_decorators = [token_required]

    def get(self, zone_id):
        current_zone = DBZone.query.get(zone_id)
        args = dns_zone_common_parser.parse_args()
        return { 'message' : "哈哈哈哈哈哈" }, 200

    def put(self, zone_id):
        current_zone = DBZone.query.get(zone_id)
        if not current_zone:
            abort(404)
        args = dns_zone_common_parser.parse_args()
        try:
            self._update_zone(current_zone, args)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200

    def delete(self, zone_id):
        current_zone = DBZone.query.get(zone_id)
        try:
            self._delete_view(current_zone)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(message='Failed', error="{e}".format(e=str(e))), 200
        return dict(message='OK'), 200

    def _update_zone(self, current_zone, args):
        pre_views = current_zone.views
        log = DBOperationLog(operation_type='修改', operator=g.current_user.username, target_type='Zone', target_name=current_zone.name, \
                target_id=int(current_zone.id), target_detail=ResourceContent.getZoneContent(current_zone, prefix="修改前："))
        db.session.add(log)
        if args['zone_type'] == 'forward only':
            current_zone.forwarders = '; '.join([ip.strip() for ip in args['forwarders'].strip().split()]) + ';'
        current_zone.name = args['name']
        current_zone.zone_group = args['zone_group']
        current_zone.zone_type = args['zone_type']
        # current_zone.forwarders = args['forwarders']
        db.session.add(current_zone)

        current_view_zones = DBViewZone.query.filter(DBViewZone.zone_id==current_zone.id).all()
        for cvz in current_view_zones:
            db.session.delete(cvz)
        for view_id in args['view_ids']:
            vz = DBViewZone(zone_id=current_zone.id, view_id=int(view_id))
            db.session.add(vz)
        db.session.flush()
        current_zone.modify(pre_views)

    def _delete_zone(self, view):
        log = DBOperationLog(operation_type='删除', operator=g.current_user.username, target_type='View', target_name=view.name, \
                target_id=int(view.id), target_detail=ResourceContent.getViewContent(view))
        db.session.add(log)
        db.session.delete(view)
        view_list = db.session.query(DBView).all()
        view.make_view('delete', view_list)


