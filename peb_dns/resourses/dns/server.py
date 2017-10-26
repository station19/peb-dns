from flask_restful import Api, Resource, url_for, reqparse, abort
from flask import Blueprint, request, jsonify, current_app
from ldap3 import Server, Connection, ALL
import datetime
import jwt
from peb_dns.models.dns import Server
from peb_dns.common.decorators import token_required
from peb_dns import db


print('xxxxxxxxxxxxxxxxxxxxxxxxx')


class DNSServerList(Resource):

    method_decorators = [token_required] 

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type = str, location = 'json')
        self.reqparse.add_argument('password', type = str, location = 'json')
        super(DNSServerList, self).__init__()

    def get(self):
        return { 'message' : "aaaaaaaaaaaaaa" }, 200

    def post(self):
        args = self.reqparse.parse_args()
        print(args)
        return { 'message': 'bbbbbbbbbbbbbbbb' }



class DNSServer(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type = str, location = 'json')
        self.reqparse.add_argument('password', type = str, location = 'json')
        super(DNSServer, self).__init__()

    def get(self):
        return { 'message' : "哈哈哈哈哈哈" }, 200

    def post(self):
        args = self.reqparse.parse_args()
        print(args)
        return { 'message': '啦啦啦啦啦啦啦啦啦' }

