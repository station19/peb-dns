from flask import Flask, Blueprint
from flask_restful import Api

page_bp = Blueprint('page', __name__, url_prefix='/page')

page_api = Api(page_bp)


from .menu import MenuSidebar
from .dashboard import ResourceAmount, DNSServerResolveRate, DNSServerStatus


page_api.add_resource(MenuSidebar, '/menu_sidebar')
page_api.add_resource(ResourceAmount, '/resource_amount')
page_api.add_resource(DNSServerResolveRate, '/servers_resolverate')
page_api.add_resource(DNSServerStatus, '/server_status')

