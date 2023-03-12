from ldap3 import Connection, SAFE_SYNC, Server, MODIFY_REPLACE
from ldap3 import get_config_parameter, set_config_parameter

from bancapis.abc.auth import ADUserStore, get_setting, ensure_user_principal_name


def connect_to_domain(type: str, ip: str, port: str, username: str, password: str):
    # server = Server(f'ldap://10.106.120.57:389')
    # conn = Connection(server, 'adm-alhomani', 'P@ssw0rd@85', client_strategy=SAFE_SYNC, auto_bind=False)
    from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
    from ldap3 import Connection, SAFE_SYNC, Server
    try:
        server = Server(f'{type}://{ip}:{port}')
        conn = Connection(server, f'{username}', f'{password}', client_strategy=SAFE_SYNC, auto_bind=False)
        conn.bind()
        return conn
    except BaseException as exception:
        print(exception)
        return None

    # connect_to_domain(type='ldap', ip='10.106.120.57',port='389', username='adm-alhomani', password='P@ssw0rd@85')


def modify_user(admin_user=None, admin_password=None, domain=None):
    from ldap3 import MODIFY_REPLACE
    # perform the Modify operation
    print("Modify user")

    store = ADUserStore(username=admin_user, password=admin_password, domain=domain)
    if not admin_user:
        admin_user = get_setting(domain, 'ABC_AUTH_ADMIN_USER')
        admin_password = get_setting(domain, 'ABC_AUTH_ADMIN_PASSWORD')

        admin_user, _domain = ensure_user_principal_name(admin_user, domain)

        store = ADUserStore(username=admin_user, password=admin_password, domain=_domain)
        attributes = store.get_attributes_for('dmugariri', domain)
        print("hello")
        return store
    else :
        admin_user, _domain = ensure_user_principal_name(admin_user, domain)
        return store