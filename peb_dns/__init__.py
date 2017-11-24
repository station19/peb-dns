from flask import Flask, Blueprint, request
from configs.config import config, config_pyfiles
from flask_migrate import Migrate, MigrateCommand
from .extensions import mail, db
from flask_cors import CORS
from .resourses.account import auth_bp
from .resourses.admin import admin
from .resourses.dns import dns_bp
from .resourses.page import page_bp
import os
import click
from .models.mappings import ROLE_MAPPINGS, DefaultPrivilege
from .models.account import DBUser, DBUserRole, DBRole, DBLocalAuth, \
                            DBPrivilege, DBRolePrivilege


APP_NAME = 'PEB-DNS'

def configure_extensions(app):
    mail.init_app(app)
    db.init_app(app)
    migrate = Migrate(app, db)

def configure_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

def configure_error_handlers(app):
    pass

def configure_hooks(app):
    pass

def configure_crossdomain(app):
    CORS(app, supports_credentials=True)

def create_app(config_name='default'):
    app = Flask(APP_NAME)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config.from_pyfile(config_pyfiles[config_name])
    app.config.from_pyfile('configs/dns_templates.cfg')
    configure_extensions(app)
    configure_blueprints(app, [auth_bp, dns_bp, admin, page_bp])
    configure_error_handlers(app)
    # configure_hooks(app)
    configure_crossdomain(app)
    return app

