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
dns_zone_common_parser.add_argument('view_ids', type = list, location = 'json', required=True)



unique_zone = db.session.query(Zone).filter(and_(Zone.name==z_name.strip(), Zone.is_inner.in_((1,2)))).first()
if unique_zone:
    return jsonify(message='Failed', error_msg='创建失败 !<br \>重复的Zone！！<br> 相同名字的Zone，每种类型域名下只能存在一个！。')

if z_type == 'forward only':
    z_forwarders = '; '.join([ip.strip() for ip in z_forwarders.strip().split()]) + ';'
new_zone = Zone(name=z_name.strip(), z_type=z_type.strip(), is_inner=int(z_is_inner), views=','.join(z_views), forwarders=z_forwarders)
db.session.add(new_zone)
db.session.flush()
log = Logs(operation_type='添加', operator=g.current_user.username, target_type='Zone', target_name=new_zone.name, \
        target_id=int(new_zone.id), target_detail=ResourceContent.getZoneContent(new_zone))
db.session.add(log)

try:
    DNSZone(action, new_zone).create()
except Exception as e:
    db.session.rollback()
    return jsonify(message='Failed', error_msg='创建失败 !!!<br> 错误信息如下：<br>' + str(e))
db.session.commit()

# 初始化 NS 域名
# @ 86400 IN NS master.a.pa.com
if new_zone.z_type != "forward only":
    for z_view in z_views:
        ns_record = Record(host='@', record_type='NS', value='master.'+new_zone.name+'.' , \
                TTL='86400', line_type=z_view, creator=g.current_user.username)
        new_zone.records.append(ns_record)
db.session.add(new_zone)
db.session.commit()

return jsonify(message='OK'), 200




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
        unique_zone = db.session.query(DBZone).filter(and_(DBZone.name==z_name.strip(), DBZone.is_inner.in_((1,2)))).first()
        if unique_zone:
            return jsonify(message='Failed', error_msg='创建失败！重复的Zone！！相同名字的Zone，每种类型域名下只能存在一个！')
        if args['zone_type'] == 'forward only':
            args['forwarders'] = '; '.join([ip.strip() for ip in args['forwarders'].strip().split()]) + ';'
        new_zone = DBZone(**args)
        db.session.add(new_zone)
        db.session.flush()
        log = DBOperationLog(operation_type='添加', operator=g.current_user.username, target_type='Zone', target_name=new_zone.name, \
                target_id=int(new_zone.id), target_detail=ResourceContent.getZoneContent(new_zone))
        db.session.add(log)
        for view_id in view_ids:
            v = DBViewZone(view_id=view_id, zone_id=new_zone.id)
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
        pre_views = current_zone._get_related_views()
        log = DBOperationLog(operation_type='修改', operator=g.current_user.username, target_type='Zone', target_name=current_zone.name, \
                target_id=int(current_zone.id), target_detail=ResourceContent.getZoneContent(current_zone, prefix="修改前："))
        db.session.add(log)
        if args['zone_type'] == 'forward only':
            args['forwarders'] = '; '.join([ip.strip() for ip in args['forwarders'].strip().split()]) + ';'
        current_zone.name = args['name']
        current_zone.zone_group = args['zone_group']
        current_zone.zone_type = args['zone_type']
        current_zone.forwarders = args['forwarders']
        db.session.add(current_zone)
        db.session.flush()
        DBViewZone.query.filter(zone_id=current_zone.id).all()
        args['view_ids']
        current_zone.modify(pre_views)


    def _delete_zone(self, view):
        log = DBOperationLog(operation_type='删除', operator=g.current_user.username, target_type='View', target_name=view.name, \
                target_id=int(view.id), target_detail=ResourceContent.getViewContent(view))
        db.session.add(log)
        db.session.delete(view)
        view_list = db.session.query(DBView).all()
        view.make_view('delete', view_list)






    # print('modify')
    zone_id = req.get('zone_id')
    if not g.current_user.can_update(Resource.ZONE, int(zone_id)):
        abort(403)
    unique_zone = db.session.query(Zone).filter(and_(Zone.name==z_name.strip(), Zone.is_inner.in_((1,2))), Zone.id != int(zone_id)).first()
    if unique_zone:
        return jsonify(message='Failed', error_msg='创建失败 !<br \>重复的Zone！！<br> 相同名字的Zone，每种类型域名下只能存在一个！。')

    m_zone = Zone.query.get(int(zone_id))
    log = Logs(operation_type='修改', operator=g.current_user.username, target_type='Zone', target_name=m_zone.name, \
            target_id=int(m_zone.id), target_detail=ResourceContent.getZoneContent(current_server, prefix="修改前："))
    db.session.add(log)

    pre_views = m_zone.views.split(',')
    record_list = m_zone.records
    m_zone.name = z_name.strip()
    m_zone.z_type = z_type
    m_zone.is_inner = int(z_is_inner)
    m_zone.views = ','.join(z_views)
    if m_zone.z_type == 'forward only':
        m_zone.forwarders = '; '.join([ip.strip() for ip in z_forwarders.strip().split()]) + ';'
    # m_zone.z_forwarders = z_forwarders.split()
    db.session.add(m_zone)

    # 清除当前zone 解除绑定view所对应的record
    del_views = set(pre_views) - set(z_views)
    del_records = db.session.query(Record).filter(Record.zone_id==m_zone.id, Record.line_type.in_(tuple(del_views))).all()
    for del_record in del_records:
        db.session.delete(del_record)

    # 添加当前zone新增绑定view时候，所对应的默认record （默认host为@的record）
    add_views = set(z_views) - set(pre_views)
    for add_view in add_views:
        ns_record = Record(host='@', record_type='NS', value='master.'+m_zone.name+'.' , \
                TTL='86400', line_type=add_view, creator=g.current_user.username)
        m_zone.records.append(ns_record)
    db.session.add(m_zone)

    try:
        DNSZone(action, m_zone).modify(pre_views)
    except Exception as e:
        db.session.rollback()
        return jsonify(message='Failed', error_msg='修改失败 !!!<br> 错误信息如下：<br>' + str(e))

    db.session.commit()
    return jsonify(message='OK'), 200
