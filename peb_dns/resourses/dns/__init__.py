
from flask import Flask, Blueprint
from flask_restful import Api

dns_bp = Blueprint('dns', __name__, url_prefix='/dns')

dns_api = Api(dns_bp)


from .server import DNSServerList, DNSServer
dns_api.add_resource(DNSServerList, '/servers')
dns_api.add_resource(DNSServer, '/servers/<int:id>')



