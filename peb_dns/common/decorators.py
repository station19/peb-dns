from functools import wraps
from flask_restful import Api, Resource, url_for, reqparse, abort
from flask import current_app, g, request
import jwt
from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord, DBDNSServer
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege, DBLocalAuth
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING
from sqlalchemy import and_, or_
from peb_dns import db

# def permission_required(permission):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             if not g.current_user.can(permission):
#                 abort(403)
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator


def permission_required(operation_type, resource_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # if not g.current_user.can(permission):
            #     abort(403)
            if resource_type == ResourceType.ZONE:
                r = DBZone
            elif resource_type == ResourceType.VIEW:
                r = DBView
            elif resource_type == ResourceType.RECORD:
                r = DBRecord
            elif resource_type == ResourceType.SERVER:
                r = DBDNSServer
            current_user_resources = db.session.query(r) \
                .join(DBPrivilege, and_(r.id == args[0], r.id == DBPrivilege.resource_id, DBPrivilege.resource_type == resource_type, DBPrivilege.operation == Operation.DELETE)) \
                .join(DBRolePrivilege, and_(DBPrivilege.id == DBRolePrivilege.privilege_id)) \
                .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
                .join(DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
                .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
                .filter(DBUser.id == g.current_user.id).all()
            if not current_user_resources:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def access_permission_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user.can_access_zone(*args, **kwargs):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # token = request.args.get('token') #http://127.0.0.1:5000/route?token=alshfjfjdklsfj89549834ur
        token = request.headers.get('Authorization')
        if not token:
            return {'message' : 'Token is missing!'}, 403
        try: 
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
        except:
            return {'message' : 'Token is invalid!'}, 403
        g.current_user = DBUser.query.filter_by(username=data.get('user')).first()
        if g.current_user is None:
            return {'message' : 'Token is invalid!'}, 403
        return f(*args, **kwargs)
    return decorated
