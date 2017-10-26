from flask import Flask, Blueprint
from flask_restful import Api

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

auth_api = Api(auth_bp)


from .auth import AuthLDAP, AuthLocal
auth_api.add_resource(AuthLDAP, '/login_ldap')
auth_api.add_resource(AuthLocal, '/login_local')


