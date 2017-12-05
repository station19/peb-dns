from peb_dns import create_app
from peb_dns.extensions import mail, db
from peb_dns.models.mappings import ROLE_MAPPINGS, DefaultPrivilege
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBLocalAuth, \
                            DBPrivilege, DBRolePrivilege

app = create_app()


def init_privilege():
    """init the default privilege data when you first time start the app."""
    privilege_count = db.session.query(DBPrivilege).count()
    if privilege_count < 1:
        print('initing the default privileges...')
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
    """init the default user and role data when you first time start the app."""
    auth_user_count = db.session.query(DBLocalAuth).count()
    local_user_count = db.session.query(DBUser).count()
    if auth_user_count < 1 and local_user_count < 1:
        print('initing the default users...')
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
        print('initing the default roles...')
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

@app.cli.command('initdb')
def initdb_command():
    """init the default data in database when you first time start the app."""
    with app.app_context(): 
        init_user_role(app)
        init_privilege()
        db.session.commit()
    print('done.')
