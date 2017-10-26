from flask import Flask, Blueprint
from flask_restful import Api
# from . import auth

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')



# from .auth import *