import bancapis

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.db.models import F
from future.builtins import super

from ldap3 import Server, Connection, ALL, SUBTREE, NTLM
from ldap3.core.exceptions import LDAPException, LDAPBindError


def import_from(module, name):
    module = __import__(module, fromlist=[name])
    return getattr(module, name)


def import_name(string):
    string = string.strip()
    tokens = string.split(".")
    if len(tokens) == 1:
        return __import__(string)
    elif len(tokens) > 1:
        return import_from(".".join(tokens[:-1]).strip(), tokens[-1].strip())
    else:
        raise ImportError('Invalid import string: {}'.format(string))

    return import_from(tokens)


ABC_AUTH_CONFIGURATIONS = settings.ABC_AUTH_CONFIGURATIONS


def get_setting(domain, key, default=None):
    possible_configs = [config for config in ABC_AUTH_CONFIGURATIONS if domain in config['DOMAINS']]

    if len(possible_configs) == 0:
        raise RuntimeError('Domain not found')
    elif len(possible_configs) > 1:
        raise AssertionError('Domains not properly configured: Duplicate entries')
    else:
        config = possible_configs[0]
    try:
        return config[key]
    except KeyError:
        if default is None:
            raise AttributeError(f'Setting "{key}" is not defined in settings.py')
        return default


AD_ATTRIBUTE_FULL_NAME = 'cn'
AD_ATTRIBUTE_USERNAME = "sAMAccountName"
AD_ATTRIBUTE_FIRST_NAME = "givenName"
AD_ATTRIBUTE_LAST_NAME = "sn"
AD_ATTRIBUTE_TITLE = "title"
AD_ATTRIBUTE_DEPARTMENT = "department"
AD_ATTRIBUTE_DESCRIPTION = "description"
AD_ATTRIBUTE_STREET_ADDRESS = "streetAddress"
AD_ATTRIBUTE_CITY = "l"
AD_ATTRIBUTE_BAD_PASSWORD_COUNT = 'badPwdCount'
AD_ATTRIBUTE_LOCKOUT_TIME = 'lockoutTime'
AD_ATTRIBUTE_TELEPHONE = "telephoneNumber"
AD_ATTRIBUTE_OTHER_MOBILE = "otherMobile"
AD_ATTRIBUTE_EMAIL = "mail"
AD_ATTRIBUTE_USER_PRINCIPAL_NAME = 'userPrincipalName'

AD_USER_ATTRIBUTES = [
    AD_ATTRIBUTE_FULL_NAME, AD_ATTRIBUTE_USERNAME, AD_ATTRIBUTE_FIRST_NAME, AD_ATTRIBUTE_LAST_NAME,
    AD_ATTRIBUTE_TITLE, AD_ATTRIBUTE_DEPARTMENT, AD_ATTRIBUTE_DESCRIPTION, AD_ATTRIBUTE_STREET_ADDRESS,
    AD_ATTRIBUTE_CITY, AD_ATTRIBUTE_BAD_PASSWORD_COUNT, AD_ATTRIBUTE_TELEPHONE, AD_ATTRIBUTE_OTHER_MOBILE,
    AD_ATTRIBUTE_EMAIL, AD_ATTRIBUTE_LOCKOUT_TIME,
    AD_ATTRIBUTE_USER_PRINCIPAL_NAME
]


def ldap_getattr(attributes, name):
    try:
        attr = attributes[name]
        if attr:
            return attr[0]
    except BaseException:
        pass
    return None


def ensure_user_principal_name(username, domain=None):
    if '@' not in username:
        if not domain:
            raise RuntimeError(f"Invalid user principal name '{username}'")
        else:
            username = f"{username}@{domain}"
    return (username, username.split('@')[-1])


def ldap_authenticate_user(username, password, domain=None, attributes=[]):
    username, domain = ensure_user_principal_name(username, domain)
    try:
        success, connection = get_ldap_connection(username, password, domain=domain)
        if not success:
            return (False, None)
        elif attributes:
            code, result = get_ldap_attributes(connection, username, domain=domain, attributes=attributes)
            if code != 0:
                return (False, None)
            else:
                return (True, result)
        else:
            connection.unbind()
            return (True, None)
    except BaseException as e:
        print("User authenticate couldn't be completed {}".format(e))
        # ems.views.send_email("User {} failed to login: error = {}".format(username,e),BancTracker.settings.EMAIL_HOST_USER)
        return (False, None)


from datetime import datetime


def validate_principal_username(username):
    assert '@' in username, f"Invalid user principal name{username}"


def resolve_domain_name(username, domain=None):
    # Resolve domain and username
    username_domain = username.splits('@')
    if len(username_domain) > 1:
        username = username
        domain = domain if domain else username_domain[1]

    if not domain:
        domain = 'bancabc.co.zw'

    return (username, domain)


def get_ldap_server(domain):
    """
        Get LDAP server for specified domain
    """
    assert domain is not None
    address = get_setting(domain, 'ABC_AUTH_ACTIVE_DIRECTORY_ADDRESS')
    print(address)
    return Server(get_setting(domain, 'ABC_AUTH_ACTIVE_DIRECTORY_ADDRESS'),
                  get_info=ALL)  # Get ldap server from its url


def get_ldap_connection(username, password, domain=None, server=None):
    username, domain = ensure_user_principal_name(username, domain)

    # Resolve domain and username
    print("Try authenticate {}".format(username))
    try:
        if server is None:
            server = get_ldap_server(domain)
        a = datetime.now()
        account_name = username.split('@')[0]
        connection = Connection(server, user=f"{get_setting(domain, 'ABC_AUTH_DOMAIN_USER_PREFIX')}\\{account_name}",
                                password=password, auto_bind=True,
                                authentication=NTLM)
        print(connection)
        b = datetime.now()
        print("Authentication successiful in {} secons".format((b - a).total_seconds()))
        return (True, connection)
    except LDAPBindError as e:
        print("Authentication failed:{}".format(e))
        return (False, None)
    except LDAPException as e:
        print('LDAP Connection error:{}'.format(e))
        raise
    except BaseException as e:
        print('Other error:{}'.format(e))
        raise
        print("User authenticate couldn't be completed")
        # ems.views.send_email("User {} failed to login: error = {}".format(username,e),BancTracker.settings.EMAIL_HOST_USER)
    return (False, None)


def get_username_transforms(username):
    lower = username.lower()
    upper = username.upper()
    capitalized = username.capitalize()
    capital2 = username[:2].upper() + username[2:].lower()

    return [lower, upper, capitalized, capital2]


def get_ldap_search_string(username):
    variations = get_username_transforms(username)
    tokens = []
    for token in variations:
        tokens.append(f'(userPrincipalName={username})')
        tokens.append(f'(sAMAccountName={username.split("@")[0]})')
    user_filter = "".join(tokens)
    search_string = f'(&(objectclass=person)(|{user_filter}))'
    print(search_string)
    return search_string


def get_ldap_attributes(connection=None, username=None, domain=None, attributes=['*'], auto_unbind=False,
                        credentials=None,
                        default=None):
    username, domain = ensure_user_principal_name(username, domain)

    from datetime import datetime
    start = datetime.now()
    if attributes is None:
        raise ValueError('Attributes cannot be NoneType, supply empty list instead')
    elif isinstance(attributes, str):
        attributes = [attributes]
    if connection is None:
        success, connection = get_ldap_connection(credentials[0], credentials[1])
        if not success:
            return (False, None)

    if '*' in attributes:
        attributes = AD_USER_ATTRIBUTES if default is None else default
    if not ('sAMAccountName' in attributes):
        attributes.append('sAMAccountName')
    if not ('userPrincipalName' in attributes):
        attributes.append('userPrincipalName')

    print("Getting user attributes")
    try:
        success = connection.search(get_setting(domain, 'ABC_AUTH_DOMAIN_DC_CONSTANT'),
                                    get_ldap_search_string(username), attributes=attributes)
        end = datetime.now()
        print(f'Attribute fetching completed in {(end - start).total_seconds()} seconds')
        users = {}
        if success:
            print("Connection estabilished")
            # Convert search results to json object where

            for entry in connection.entries:
                entry = json.loads(entry.entry_to_json())["attributes"]
                if not entry["userPrincipalName"]:
                    continue
                print("Get attributes for {}".format(entry["userPrincipalName"][0]))
                user = {}
                for prop in entry:
                    try:
                        user[prop] = entry[prop][0]
                    except BaseException:
                        user[prop] = None
                users[entry["userPrincipalName"][0]] = user

            return (True, users)
        else:
            return (False, None)
    except BaseException:
        raise
    finally:
        if auto_unbind:
            connection.unbind()


import json


class ADUserStore(object):
    STATUS_USER_IS_UNLOCKED = 0
    STATUS_USER_IS_LOCKED = 1
    STATUS_USER_IS_DISABLED = 2
    STATUS_USER_NOT_FOUND = 3  # For both disabled or not found
    STATUS_INVALID_ADMIN_CREDENTIALS = 4
    STATUS_UNABLE_TO_QUERY_STATUS = 5

    def __init__(self, username, password, domain=None):
        success, connection = get_ldap_connection(username, password, domain=domain)
        self.is_authenticated = success
        self.connection = connection

    def get_attributes_for(self, username, domain=None):
        if not self.is_authenticated:
            raise ValueError('Authentication failed, cannot get attributes')

        success, users = get_ldap_attributes(self.connection, username, domain=domain, attributes=AD_USER_ATTRIBUTES)
        if not success:
            raise ValueError('Could not find fetch user attributes')
        # For each user map to standard names
        proccessed = [ADUserStore.preproccess_attributes(user, domain=domain) for user in users.values()]
        return proccessed

    def unlock_account(self, username, domain=None):
        username, domain = ensure_user_principal_name(username, domain)

        if self.is_authenticated:
            success = self.connection.search(get_setting(domain, 'ABC_AUTH_DOMAIN_DC_CONSTANT'),
                                             get_ldap_search_string(username), attributes=['cn'])
            if success:
                if not self.connection.entries:
                    print("User '{}' not found".format(username))
                    return False
                user_dn = json.loads(self.connection.entries[0].entry_to_json())['dn']
                print(user_dn)
                return self.connection.extend.microsoft.unlock_account(user_dn)
            else:
                return False
        else:
            print("Authentication Error")
            return False

    @staticmethod
    def preproccess_attributes(each, domain):
        username, domain = ensure_user_principal_name(each[AD_ATTRIBUTE_USER_PRINCIPAL_NAME], domain=domain)
        user_instance = {}

        # Get username
        user_instance['username'] = each[AD_ATTRIBUTE_USERNAME]
        user_instance['user_principal_name'] = each[AD_ATTRIBUTE_USER_PRINCIPAL_NAME]

        # Get first name
        user_instance['first_name'] = each[AD_ATTRIBUTE_FIRST_NAME]

        # Get last name
        user_instance['last_name'] = each[AD_ATTRIBUTE_LAST_NAME]

        # Get full name
        user_instance['full_name'] = each[AD_ATTRIBUTE_FULL_NAME]

        # Get title
        user_instance['title'] = each[AD_ATTRIBUTE_TITLE]

        # Get department
        user_instance['department'] = each[AD_ATTRIBUTE_DEPARTMENT]

        # Get branch
        user_instance['description'] = each[AD_ATTRIBUTE_DESCRIPTION]

        # Resolve extension and resolve mobile number
        mobile_number, extension = ADUserStore.extract_contacts(each[AD_ATTRIBUTE_TELEPHONE])
        mobile_number1, extension1 = ADUserStore.extract_contacts(AD_ATTRIBUTE_OTHER_MOBILE)

        user_instance['mobile_number'] = ADUserStore.join_contacts(mobile_number, mobile_number1)
        user_instance['extension'] = ADUserStore.join_contacts(extension, extension1)

        # Guess email address
        user_instance['email_address'] = user_instance['user_principal_name']

        # Resolve work address
        user_instance['work_address'] = ADUserStore.join_contacts(each['streetAddress'], each['l'], sep="\n")

        # Resolve work address
        user_instance['bad_password_count'] = each[AD_ATTRIBUTE_BAD_PASSWORD_COUNT]

        user_instance['lockout_time'] = each[AD_ATTRIBUTE_LOCKOUT_TIME]
        return user_instance

    @staticmethod
    def check_user_status(admin_user=None, admin_password=None, user_to_check=None, domain=None):
        """
            Return - integer code
                 0 for unlocked
                 1 for locked
                 2 If admin user fails
                 3 If user not in AD
                 4 Error unknown
        """
        user_to_check, domain = ensure_user_principal_name(user_to_check, domain)

        # Firstly check credintial with external auth
        success, connection = get_ldap_connection(admin_user, admin_password)
        if not success:
            return ADUserStore.STATUS_INVALID_ADMIN_CREDENTIALS  # Admin credentials invalid
        else:
            success, users = get_ldap_attributes(connection, username=user_to_check,
                                                 attributes=[AD_ATTRIBUTE_BAD_PASSWORD_COUNT,
                                                             AD_ATTRIBUTE_LOCKOUT_TIME], domain=domain)
            if not success:
                return ADUserStore.STATUS_UNABLE_TO_QUERY_STATUS  # Unkown error, could not check state
            else:
                users = list(users.values())
                if not users:
                    return ADUserStore.STATUS_USER_NOT_FOUND  # User not found
                else:
                    bad_passwords = users[0][AD_ATTRIBUTE_BAD_PASSWORD_COUNT]
                    lockout_time = users[0][AD_ATTRIBUTE_LOCKOUT_TIME]
                    print(f'Bad password count:{bad_passwords} Lockout time: {lockout_time}')

                    if ADUserStore.islocked(bad_passwords, lockout_time, domain):
                        return ADUserStore.STATUS_USER_IS_LOCKED  # User is locked
                    else:
                        return ADUserStore.STATUS_USER_IS_UNLOCKED  # User is not locked

    @staticmethod
    def islocked(bad_passwords, lockout_time, domain):
        if int(bad_passwords) >= 3:
            return True
        if lockout_time:
            lockout_time = lockout_time.strip()
            if lockout_time.isnumeric():
                return int(lockout_time) != 0
            else:
                return lockout_time != get_setting(domain, 'ABC_AUTH_DOMAIN_UNLOCKED_LOCKOUT_TIME')
        else:
            return False

    @staticmethod
    def join_contacts(*args, sep='; '):
        args = [x for x in args if x]
        if args:
            return sep.join(args)
        else:
            return None

    @staticmethod
    def extract_contacts(string):
        def proccess(x):
            if isinstance(x, tuple):
                x = x[0]
            if len(x.strip()) >= 4:
                return x
            else:
                return None

        if not (string and string.strip() != ""):
            return (None, None)
        import re
        mobile_number = r"((\+){0,1}(263)((71)|(77)|(78))(\s*\d){7})"
        telephone_263 = r"(((\+)*(263)(\s*\-*)((7(\s*\-*)[^178])|([^7](\s*\-*)\d))(([\-\s\(\)/]*)\d)*))"
        telephone_other = r"(\+)*(([\-\s\(\)/]*[^2])|([\-\s\(\)/]*2[\-\s\(\)/]*[^6])|([\-\s\(\)/]*2[\-\s\(\)/]*6[\-\s\(\)/]*[^3]))([\-\s\(\)/]*\d)*"
        extension_8888 = r"(\d{4})"
        mobile_number2 = r"((0)(\s*((71)|(77)|(78)))(\s*\d){7})"

        string = string.strip()
        mobile_numbers = [proccess(x) for x in re.findall(mobile_number, string) if proccess(x)]
        for x in mobile_numbers:
            string = string.replace(x, "")

        telephones = [proccess(x) for x in re.findall(telephone_263, string) if proccess(x)]
        for x in telephones:
            string = string.replace(x, "")

        telephones.extend([proccess(x) for x in re.findall(telephone_other, string) if proccess(x)])

        for x in telephones:
            string = string.replace(x, "")

        mobile_numbers.extend([proccess(x) for x in re.findall(mobile_number2, string) if proccess(x)])
        for x in mobile_numbers:
            string = string.replace(x, "")

        extensions = [proccess(x) for x in re.findall(extension_8888, string) if proccess(x)]
        telephones.extend(map(lambda x: f'Ext: {x.strip()}', extensions))

        mobile_numbers = "; ".join(map(lambda x: x.strip(), mobile_numbers))

        telephones = "; ".join(map(lambda x: x.strip(), telephones))

        return (mobile_numbers, telephones)

    @staticmethod
    def predict_department(ad_department, sys_departments, ad_description=None):
        # Use inexact search as similarity measure
        from fuzzywuzzy import fuzz
        return None
        if not sys_departments:
            raise ValueError('System departments empty or none')

        # Match best department from ad_department
        best_department = None
        if ad_department:
            best_department = sorted(sys_departments, key=lambda x: fuzz.partial_ratio(x, ad_department), reverse=True)[
                0]
        # Match best department from ad_department
        elif ad_description:
            best_department = \
                sorted(sys_departments, key=lambda x: fuzz.partial_ratio(x, ad_description), reverse=True)[0]

        return best_department

    @staticmethod
    def predict_branch(ad_address, sys_branches):
        # Use inexact search as similarity measure
        from fuzzywuzzy import fuzz
        if not sys_branches:
            raise ValueError('System branches empty or none')

        # Match best department from ad_department
        best_branch = None
        if ad_address:
            best_branch = sorted(sys_branches, key=lambda x: fuzz.partial_ratio(x, ad_address), reverse=True)[0]

        return best_branch

    @staticmethod
    def authenticate_via_external_api(username, password):
        from bancapis.abc import apis
        return apis.ldap_quick_athenticate_user(username, password)

    @staticmethod
    def authenticate_via_internal_api(username, password):
        return ldap_authenticate_user(username, password)[0]


def unlock_account(username, admin_user=None, admin_password=None, domain=None):
    username, domain = ensure_user_principal_name(username, domain)
    if not admin_user:
        admin_user = get_setting(domain, 'ABC_AUTH_ADMIN_USER')
        admin_password = get_setting(domain, 'ABC_AUTH_ADMIN_PASSWORD')

    admin_user, _domain = ensure_user_principal_name(admin_user, domain)

    store = ADUserStore(username=admin_user, password=admin_password, domain=_domain)

    if store.unlock_account(username, domain=domain):
        print(f"'{username}' unlocked successfully")
        return True
    else:
        print(f"Failed to unlock '{username}'")
        return False


def bypass_account_setup_onstart(*usernames):
    from ems.models import Settings
    x = Settings.objects.filter(user__username__in=usernames).update(account_setup_onstart=False)
    return f"Affected:{x}"


def create_user(username, admin_user=None, admin_password=None, domain=None, **kwargs):
    username, domain = ensure_user_principal_name(username, domain)
    if not admin_user:
        admin_user = get_setting(domain, 'ABC_AUTH_ADMIN_USER')
        admin_password = get_setting(domain, 'ABC_AUTH_ADMIN_PASSWORD')

    store = ADUserStore(username=admin_user, password=admin_password)
    if not store.is_authenticated:
        print('Failed to connect/authenticate with AD')
        return None
    else:
        attributes = store.get_attributes_for(username, domain)

        if not attributes:
            print('User not foound "{}"'.format(username))
            return None
        else:
            attributes = attributes[0]
            if not username.endswith('bancabc.co.zw'):
                attributes['username'] = username.strip()
            if User.objects.filter(username=attributes['username']).exists():
                print("User already in system")
                return None
            callback_name = get_setting(domain, 'ABC_AUTH_AUTO_CREATE_USER_CALLBACK')
            if callback_name:
                user_constructor = import_name(callback_name)
            user = user_constructor(attributes, **kwargs)
            post_creation_callbacks = get_setting(domain, 'ABC_AUTH_POST_CREATION_CALLBACKS', [])
            for callback in post_creation_callbacks:
                import_name(callback_name)(user, **kwargs)
            return user


def read_ad_account(username, admin_user=None, admin_password=None, attributes=None, domain=None):
    username, domain = ensure_user_principal_name(username, domain)
    if not admin_user:
        admin_user = get_setting(domain, 'ABC_AUTH_ADMIN_USER')
        admin_password = get_setting(domain, 'ABC_AUTH_ADMIN_PASSWORD')

    admin_user, _domain = ensure_user_principal_name(admin_user, domain)

    if attributes is None:
        store = ADUserStore(username=admin_user, password=admin_password, domain=_domain)
        print(json.dumps(store.get_attributes_for(username, domain=domain), indent=True))
    else:
        attributes = \
        get_ldap_attributes(username=username, domain=domain, credentials=(admin_user, admin_password, _domain),
                            attributes=attributes.split(","), default=attributes.split(','))[1]
        print(json.dumps(attributes, indent=True))


class LDAPAuth(ModelBackend):
    """
    LDAP Backend to integrate and authenticate with active Directory
    """

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            raise ValueError("Username or password cannot be null")
        # Track original username as specified in request
        raw_username = username
        # Resolve account name [short-username], user principal name [mail-like] and domain
        if '@' in username:
            account_name, domain = username.split('@')
        else:
            account_name = username
            domain = "bancabc.co.zw"  # Default to BancABC ZW
            username = username + '@' + domain  # Construct user principal name

        # Get authentication backend based on domain
        try:
            DOMAIN_CONFIG = \
            [domain_config for domain_config in ABC_AUTH_CONFIGURATIONS if (domain in domain_config['DOMAINS'])][0]
        except IndexError:
            raise RuntimeError('Domain matching username not configured')

        # Force username to lower case
        if DOMAIN_CONFIG['ABC_AUTH_LOWER_CASE_USERNAME']:
            account_name = account_name.lower()
            username = username.lower()

        # Get response object
        response_object = kwargs.get('response', {})

        # Determine username: may exclude domain for ZW BancABC users
        target_username = account_name if domain == 'bancabc.co.zw' else username

        # Check if user is inactive(soft deleted)
        if User.objects.filter(username=target_username, is_active=False).exists():
            print("Inactive user", username, "denied access.")
            response_object['status_known'] = True
            response_object['not_found'] = True
            return None  # DENY ACCESS

        # Try get user from database
        try:
            user = User.objects.get(username=target_username)
        except User.DoesNotExist:
            user = None

        if DOMAIN_CONFIG['ABC_AUTH_USER_MANAGEMENT_BACKEND'] == 'DJANGO_DEFAULT_BACKEND':
            print("Try authenticate '{}' with DJANGO DEFAULT BACKEND".format(username, DOMAIN_CONFIG[
                'ABC_AUTH_USER_MANAGEMENT_BACKEND']))
            user = self.authenticate_via_django(
                request=request,
                user=user,
                username=username,
                password=password,
                response_object=response_object,
            )
        elif DOMAIN_CONFIG['ABC_AUTH_USER_MANAGEMENT_BACKEND'] == 'WINDOWS_LDAP_BACKEND':
            print("Try authenticate '{}' with WINDOWS LDAP".format(username,
                                                                   DOMAIN_CONFIG['ABC_AUTH_USER_MANAGEMENT_BACKEND']))
            user = self.authenticate_via_ldap(
                user=user,
                username=username,
                domain=domain,
                password=password,
                raw_username=username,
                response_object=response_object,
            )
        else:
            raise RuntimeError("User not found event not implemented for '{}'".format(ABC_AUTH_USER_MANAGEMENT_BACKEND))

        # Log failed authentication
        if user is None:
            print('Status code:{}'.format(response_object.get('raw_status', None)))
            print('Status known     :{}'.format(response_object.get('status_known', None)))
            print('Account locked   :{}'.format(response_object.get('is_locked', None)))
            print('Account not found:{}'.format(response_object.get('not_found', None)))

        return user

    def authenticate_via_ldap(self, user, username, password, domain=None, raw_username=None, response_object={}, ):
        # User not found
        if user is None:
            print('User not found in the system, try get user:{}'.format(username))
            if not ('@' in raw_username):
                response_object['raw_status'] = ADUserStore.STATUS_USER_NOT_FOUND
                response_object['status_known'] = True
                response_object['not_found'] = True
                response_object[
                    'hint'] = 'You are loging in for first time, you must use email address as your username.'
                # Deny Access: go return None
            elif not get_setting(domain, 'ABC_AUTH_AUTO_CREATE_USER_FROM_AD'):
                response_object['status_known'] = False
                # Deny Access: go return None
            else:
                admin_user = get_setting(domain, 'ABC_AUTH_ADMIN_USER')
                admin_password = get_setting(domain, 'ABC_AUTH_ADMIN_PASSWORD')

                # Authenticate against Active Directory
                store = ADUserStore(username=admin_user, password=admin_password)
                # Check if admin authentication was a success
                if not store.is_authenticated:
                    print('User not found in the AD, deny access:{}'.format(admin_user))
                    print("Invalid credentials", admin_user, "denied access.")
                    response_object['status_known'] = False
                    # Deny Access: go return None
                else:  # @TODO
                    print('User found in the AD, create user:{}'.format(username))
                    # Get user attributes
                    attributes = store.get_attributes_for(username)
                    if not attributes:
                        # User not found
                        response_object['raw_status'] = ADUserStore.STATUS_USER_NOT_FOUND
                        response_object['status_known'] = True
                        response_object['not_found'] = True
                        response_object['hint'] = ''
                        # Deny Access: go return None
                    else:
                        attributes = attributes[0]
                        # Remove domain prefix for ZW BancABC
                        if raw_username.endswith('bancabc.co.zw'):
                            pass  # Just use AD sMAccountName as username
                        else:
                            attributes[
                                'username'] = raw_username  # Replace AD sMAccountName with email specified by user
                        # Get function to build user
                        callback_name = get_setting(domain, 'ABC_AUTH_AUTO_CREATE_USER_CALLBACK')
                        user_constructor = import_name(callback_name)
                        # Auto create user
                        user = user_constructor(attributes)
                        return user  # GRANT ACCESS

        # Call to authenticate with LDAP
        elif ADUserStore.authenticate_via_internal_api(username, password):
            return user

        # Describe failed authentication
        elif get_setting(domain, 'ABC_AUTH_DESCRIBE_FAILED_AUTHENTICATION'):
            print("Check reason for failure")
            # Check if user exists in AD or locked (@Encrypt credentials)
            status = ADUserStore.check_user_status(
                admin_user=get_setting(domain, 'ABC_AUTH_ADMIN_USER'),
                admin_password=get_setting(domain, 'ABC_AUTH_ADMIN_PASSWORD'),
                user_to_check=username
            )
            print('Status code:{}'.format(status))
            # Get raw status code
            response_object['raw_status'] = status
            # Get transformed status-variables [status_known, is_locked, not_found]
            response_object['is_locked'] = (status == ADUserStore.STATUS_USER_IS_LOCKED)
            response_object['not_found'] = (status == ADUserStore.STATUS_USER_NOT_FOUND)
            response_object['status_known'] = not (status in [ADUserStore.STATUS_INVALID_ADMIN_CREDENTIALS,
                                                              ADUserStore.STATUS_UNABLE_TO_QUERY_STATUS])
            # Deny Access: go return None
        # Assume wrong username or password
        else:
            response_object['status_known'] = False
            # Deny Access: go return None

        return None  # Deny Access

    def authenticate_via_django(self, user, username, password, response_object, request):
        from bancapis.models import PasswordManagementRecord
        # Immidiately deny access if user not found
        if user is None:
            print("User not found", username, "denied access.")
            response_object['status_known'] = True
            response_object['not_found'] = True
            response_object['raw_status'] = ADUserStore.STATUS_USER_NOT_FOUND
            return None  # DENY ACCESS
        else:
            # Check if account is locked
            if PasswordManagementRecord.objects.filter(user=user, bad_password_count__gte=3):
                response_object['status_known'] = True
                response_object['is_locked'] = True
                response_object['raw_status'] = ADUserStore.STATUS_USER_IS_LOCKED
            # Try authenticate user: reset bad password count and grant access
            elif super(LDAPAuth, self).authenticate(request=request, username=username, password=password):
                PasswordManagementRecord.objects.filter(user=user).update(bad_password_count=0)
                return user  # Grant Access
            # Otherwise Increment bad password count
            else:
                PasswordManagementRecord.objects.filter(user=user).update(
                    bad_password_count=F("bad_password_count") + 1)
                if PasswordManagementRecord.objects.filter(user=user, bad_password_count__gte=3):
                    # Set account locked
                    response_object['status_known'] = True
                    response_object['is_locked'] = True
                    response_object['raw_status'] = ADUserStore.STATUS_USER_IS_LOCKED
                else:
                    response_object['status_known'] = True
                    response_object['is_locked'] = False
                    response_object['raw_status'] = ADUserStore.STATUS_USER_IS_UNLOCKED

            return None  # Deny Access

# python manage.py invoke ad_createuser amangeni@bancabc.com
# python manage.py invoke ad_createuser lmoodly@bancabc.com
# python manage.py invoke ad_createuser cbabariya@bancabc.com
# python manage.py invoke ad_createuser sdale@bancabc.com
# python manage.py invoke ad_createuser sntsinde@bancabc.com
# python manage.py invoke ad_createuser lnkosi@bancabc.com
# python manage.py invoke ad_createuser jzacks@bancabc.com
# python manage.py invoke ad_createuser kmourougane@bancabc.com
# python manage.py invoke ad_createuser vkmandalapu@bancabc.com
# python manage.py invoke ad_createuser prkumar@bancabc.com
# python manage.py invoke ad_createuser rrajakumari@bancabc.com
# python manage.py invoke ad_createuser lbansal@bancabc.com
# python manage.py invoke ad_createuser kbabu@bancabc.com
# python manage.py invoke ad_createuser dvrpvusa@bancabc.com
# python manage.py invoke ad_createuser dradhakrishnan@bancabc.com
# python manage.py invoke ad_createuser vareddy@bancabc.com
# python manage.py invoke ad_createuser dbharathi@bancabc.com
# python manage.py invoke ad_createuser mkiruba@bancabc.com
# python manage.py invoke ad_createuser psomase@bancabc.com
# python manage.py invoke ad_createuser preynold@bancabc.com
# python manage.py invoke ad_createuser amulyasp@bancabc.com
# python manage.py invoke ad_createuser aharalahalli@bancabc.com
# python manage.py invoke ad_createuser annapoornams@bancabc.com
# python manage.py invoke ad_createuser asrivastava@bancabc.com
# python manage.py invoke ad_createuser divyacj@bancabc.com
# python manage.py invoke ad_createuser dparida@bancabc.com
# python manage.py invoke ad_createuser achoudhary@bancabc.com
# python manage.py invoke ad_createuser aagrawal@bancabc.com
# python manage.py invoke ad_createuser tkgalane@bancabc.com
# python manage.py invoke ad_createuser shenning@bancabc.com
# python manage.py invoke ad_createuser sntsinde@bancabc.com
# python manage.py invoke ad_createuser amangeni@bancabc.com
# python manage.py invoke ad_createuser mtaylor@bancabc.com
# python manage.py invoke ad_createuser arburger@bancabc.com
# python manage.py invoke ad_createuser abraimo@bancabc.com
# python manage.py invoke ad_createuser amuzembe@bancabc.com
# python manage.py invoke ad_createuser cguvamombe@bancabc.com
# python manage.py invoke ad_createuser dsianga@bancabc.com
# python manage.py invoke ad_createuser djeke@bancabc.com
# python manage.py invoke ad_createuser ewilson1@bancabc.com
# python manage.py invoke ad_createuser fmarara@bancabc.com
# python manage.py invoke ad_createuser mkangwa@bancabc.com
# python manage.py invoke ad_createuser rosupile@bancabc.com
# python manage.py invoke ad_createuser ssafinieli@bancabc.com
# python manage.py invoke ad_createuser ewilson1@bancabc.com
# python manage.py invoke ad_createuser mhadamjee@bancabc.com
# python manage.py invoke ad_createuser ssamuel@bancabc.com
# python manage.py invoke ad_createuser siddi@bancabc.co.zm
# python manage.py invoke ad_createuser kkabwe@bancabc.co.zm
# python manage.py invoke ad_createuser mkaunda@bancabc.com
# python manage.py invoke ad_createuser msitali@bancabc.com
# python manage.py invoke ad_createuser nnyangu@bancabc.co.zm
# python manage.py invoke ad_createuser rsilavwe@bancabc.com
# python manage.py invoke ad_createuser emulundano@bancabc.com
# python manage.py invoke ad_createuser fmazuzu@bancabc.co.zw
# python manage.py invoke ad_createuser tchoga@bancabc.co.zw
# python manage.py invoke ad_createuser mziki@bancabc.co.zw
# python manage.py invoke ad_createuser gchinamona@bancabc.co.zw
# python manage.py invoke ad_createuser cguvamombe@bancabc.co.zw
# python manage.py invoke ad_createuser alhomani@bancabc.com
# python manage.py invoke ad_createuser cdjanasi@bancabc.com
# python manage.py invoke ad_createuser enhacume@bancabc.com
# python manage.py invoke ad_createuser esacate@bancabc.com
# python manage.py invoke ad_createuser oguilunzo@bancabc.com
# python manage.py invoke ad_createuser wmachiana@bancabc.com


# python manage.py invoke ad_createuser <accountname@domain>

# python manage.py invoke ad_readaccount <accountname@domain>

# python manage.py invoke ad_unlockaccount <accountname@domain>

# python manage.py invoke ems.users.authorize_users <accountname@domain>

# python manage.py invoke bancapis.abc.auth.bypass_account_setup_onstart <username>
