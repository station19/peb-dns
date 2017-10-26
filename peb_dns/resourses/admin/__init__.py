from flask import Blueprint, request, jsonify, current_app
from flask_restful import Api, Resource, url_for

admin = Blueprint('admin', __name__, url_prefix='/admin')

admin_api = Api(admin)

