from flask import Blueprint, request, jsonify, current_app
from flask_restful import Api, Resource, url_for

dns = Blueprint('dns', __name__, url_prefix='/dns')

dns_api = Api(dns)