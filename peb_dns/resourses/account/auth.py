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
        super(AuthLocal, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type = str, 
                                    location = 'json', required=True)
        self.reqparse.add_argument('password', type = str, 
                                    location = 'json', required=True)
        self.reqparse.add_argument('password2', type = str, 
                                    location = 'json', required=True)
        self.reqparse.add_argument('email', type = str, 
                                    location = 'json', required=True)

    def get(self):
        get_args = request.args
        auth_user = DBLocalAuth.query.filter_by(
            username = get_args['username']).first()
        if auth_user is None:
            return { 'message' : "认证失败！用户不存在！" }, 401
        if not auth_user.verify_password(get_args['password']) :
            return { 'message' : "认证失败！账号或密码错误！" }, 401
        local_user = DBUser.query.filter_by(username=get_args['username']).first()
        token = jwt.encode({
            'user' : local_user.username, 
            'exp' : datetime.datetime.now() + datetime.timedelta(hours=24)
            }, current_app.config['SECRET_KEY'])
        return {
            'token' : token.decode('UTF-8'),
            'user_info': local_user.to_json()
            }, 200

    def post(self):
        args = self.reqparse.parse_args()
        print(args)
        auth_user = DBLocalAuth.query.filter_by(
            username = args['username']).first()
        local_user = DBUser.query.filter_by(
            username = args['username']).first()
        if auth_user or local_user:
            return { 'message': "Failed", "error": "用户已存在！" }, 400
        new_auth_user = DBLocalAuth(
            username=args['username'], email=args['email'])
        new_auth_user.password = args['password']
        new_local_user = DBUser(username=args['username'], email=args['email'])
        db.session.add(new_local_user)
        db.session.add(new_auth_user)
        db.session.commit()
        return { 'message': "OK" }, 200
        
