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
from .models.mappings import ROLE_MAPPINGS
from .models.account import DBUser, DBUserRole, DBRole, DBLocalAuth


APP_NAME = 'PEB-DNS'

def configure_extensions(app):
    mail.init_app(app)
    db.init_app(app)
    migrate = Migrate(app, db)


def configure_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_db(app):
    with app.app_context(): 
        auth_user_count = db.session.query(DBLocalAuth).count()
        local_user_count = db.session.query(DBUser).count()
        if auth_user_count < 1 and local_user_count < 1:
            default_admin = DBLocalAuth(
                id=ROLE_MAPPINGS['admin'], 
                username=app.config.get("DEFAULT_ADMIN_USERNAME"),
                email=app.config.get("DEFAULT_ADMIN_EMAIL")
                )
            default_admin.password = app.config.get("DEFAULT_ADMIN_PASSWD")
            default_admin_local = DBUser(
                id=ROLE_MAPPINGS['admin'], 
                username=app.config.get("DEFAULT_ADMIN_USERNAME"),
                email=app.config.get("DEFAULT_ADMIN_EMAIL")
                )
            db.session.add(default_admin)
            db.session.add(default_admin_local)
        role_count = db.session.query(DBRole).count()
        if role_count < 1:
            for k,v in ROLE_MAPPINGS:
                new_role = DBRole(id=v, name=k)
                db.session.add(new_role)
        user_role_count = db.session.query(DBUserRole).count()
        if role_count < 1:
            admin_user_role = DBUserRole(
                id=ROLE_MAPPINGS['admin'], 
                user_id=ROLE_MAPPINGS['admin'], 
                role_id=ROLE_MAPPINGS['admin'], 
                )
            db.session.add(admin_user_role)
        db.session.commit()


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
    # configure_db(app)
    # configure_hooks(app)
    configure_crossdomain(app)

    return app

