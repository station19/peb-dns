from flask import Blueprint, request, jsonify, current_app
from flask_restful import Api, Resource, url_for

admin = Blueprint('admin', __name__, url_prefix='/admin')

admin_api = Api(admin)

from .user import UserList, User
admin_api.add_resource(UserList, '/users')
admin_api.add_resource(User, '/users/<int:user_id>')

from .role import RoleList, Role
admin_api.add_resource(RoleList, '/roles')
admin_api.add_resource(Role, '/roles/<int:role_id>')
