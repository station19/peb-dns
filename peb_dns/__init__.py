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

def init_privilege():
    privilege_count = db.session.query(DBPrivilege).count()
    if privilege_count < 1:
        default_privileges = [
            DefaultPrivilege.SERVER_ADD,
            DefaultPrivilege.ZONE_ADD,
            DefaultPrivilege.VIEW_ADD,
            DefaultPrivilege.BIND_CONF_EDIT
            ]
        for p in default_privileges:
            new_p = DBPrivilege(name=p)
            db.session.add(new_p)
            db.session.flush()
            admin_rp =  DBRolePrivilege(
                                role_id=ROLE_MAPPINGS['admin'],
                                privilege_id=new_p.id
                                )
            db.session.add(admin_rp)
            if p == DefaultPrivilege.SERVER_ADD:
                server_admim_rp =  DBRolePrivilege(
                                    role_id=ROLE_MAPPINGS['server_admin'],
                                    privilege_id=new_p.id
                                    )
                db.session.add(server_admim_rp)
            if p == DefaultPrivilege.ZONE_ADD:
                zone_admin_rp =  DBRolePrivilege(
                                    role_id=ROLE_MAPPINGS['zone_admin'],
                                    privilege_id=new_p.id
                                    )
                db.session.add(zone_admin_rp)
            if p == DefaultPrivilege.VIEW_ADD:
                view_admin_rp =  DBRolePrivilege(
                                    role_id=ROLE_MAPPINGS['view_admin'],
                                    privilege_id=new_p.id
                                    )
                db.session.add(view_admin_rp)

def init_user_role(app):
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
        for k,v in ROLE_MAPPINGS.items():
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

def configure_error_handlers(app):
    pass

def configure_hooks(app):
    @app.before_first_request
    def init_db_data():
        with app.app_context(): 
            init_user_role(app)
            init_privilege()
            db.session.commit()

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
    configure_hooks(app)
    configure_crossdomain(app)
    return app

