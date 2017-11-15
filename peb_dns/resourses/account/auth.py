from flask_restful import Api, Resource, url_for, reqparse, abort
from flask import Blueprint, request, jsonify, current_app
from ldap3 import Connection, ALL
from ldap3 import Server as LDAPServer
import datetime
import jwt
from peb_dns.models.account import DBUser, DBLocalAuth
from peb_dns import db


class AuthLDAP(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type = str, location = 'json')
        self.reqparse.add_argument('password', type = str, location = 'json')
        super(AuthLDAP, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        username, password = args['username'], args['password']
        if self._auth_via_ldap(username, password):
            user = DBUser.query.filter_by(username=username).first()
            if user is not None :
                token = jwt.encode({
                    'user' : user.username, 
                    'exp' : datetime.datetime.now() + datetime.timedelta(hours=24)
                    }, current_app.config['SECRET_KEY'])
                return {
                    'token' : token.decode('UTF-8'), 
                    'user_info': user.to_json()
                    }, 200
            new_user = DBUser(username=username)
            db.session.add(new_user)
            db.session.commit()
            token = jwt.encode({
                'user' : new_user.username,
                'exp' : datetime.datetime.now() + datetime.timedelta(hours=24)
                }, current_app.config['SECRET_KEY'])
            return {
                'token' : token.decode('UTF-8'),
                'user_info': new_user.to_json()
                }, 200
        return { 'message' : "认证失败！"}, 401

    def _auth_via_ldap(self, username, passwd):
        try:
            server = LDAPServer(
                current_app.config.get('LDAP_SERVER'), 
                port=int(current_app.config.get('LDAP_SERVER_PORT')
                ), use_ssl=True, get_info=ALL)
            _connection = Connection(
                server, 
                'cn=' + username + current_app.config.get('LDAP_CONFIG'), 
                passwd, 
                auto_bind=True
                )
        except Exception as e:
            return False
        return True


class AuthLocal(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type = str, location = 'json')
        self.reqparse.add_argument('password', type = str, location = 'json')
        super(AuthLocal, self).__init__()

    def post(self, login_url_postfix):

        args = self.reqparse.parse_args()
        auth_user = DBLocalAuth.query.filter_by(username = args['username'])
        if auth_user is None:
            return { 'message' : "认证失败！" }, 401
        if auth_user.verify_password(args['password']) :
            return { 'message' : "认证失败！" }, 401
        token = jwt.encode({
            'user' : auth_user.username, 
            'exp' : datetime.datetime.now() + datetime.timedelta(hours=24)
            }, current_app.config['SECRET_KEY'])
        return {'token':token, 'user_info': auth_user.to_json()}, 200


