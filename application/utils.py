from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from ldap3.core.exceptions import LDAPSocketOpenError

from application.models import Profile


def get_user_for_login(request, username, password, auth_response):
    try:
        user = authenticate(
            request,
            username=username,
            password=password,
            response=auth_response,
        )
        return user
    except LDAPSocketOpenError:

        print('Domain not available')
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            print("user does not exist locally")
            return None
        except BaseException as e:
            print(e)
            return None
    except BaseException as e:
        print(e)
        return None


def create_user(username=None, first_name=None, last_name=None, email_address=None, ):
    """
        Create user object
        Arguments
            username          [Raw]
            firstname         [Raw]
            lastname          [Raw]
            title             [Raw]
            email             [Raw]
            extension         [Raw]
            mobile_number     [Raw]
            work_address    [Raw]
            department        [Model]
            sub_department    [Model]
            branch            [Model]
    """
    # Check if user exists

    if User.objects.filter(username=username).exists():
        return None, 1, 'User already exists'

    # Create DJango user model
    new_user = User.objects.create_user(
        username=username,
        email=email_address,
        password='dummy_password'
    )

    # Set name
    new_user.first_name = first_name
    new_user.last_name = last_name

    # Set status
    new_user.is_staff = True
    new_user.is_active = True
    # Save changes
    new_user.save()

    # Create employee profile and link to DJango auth user
    profile = Profile.objects.get_or_create(
        user=new_user,
    )
    return new_user, 0, 'User successfully created'


def create_user_from_attributes(attributes):
    # Create user
    user, code, message = create_user(
        username=attributes['username'].lower(),
        first_name=attributes['first_name'].capitalize(),
        last_name=attributes['last_name'].capitalize(),
        email_address=attributes.get('email_address', None),
    )

    return user


def sync_with_ad():
    try:
        from bancapis.abc.auth import ADUserStore
        from bancapis.abc.auth import get_setting
        store = ADUserStore(
            username=get_setting(key='ABC_AUTH_ADMIN_USER', domain='bancabc.co.zw'),
            password=get_setting(key='ABC_AUTH_ADMIN_PASSWORD', domain='bancabc.co.zw'),
        )

        users = store.get_attributes_for('*@bancabc.co.zw')
        for user in users:
            create_user_from_attributes(user)
    except BaseException as e:
        print(e)


def ldap_modify_attributes():
    # import class and constants
    from ldap3 import Server, Connection, ALL, MODIFY_REPLACE

    # define the server
    s = Server('servername', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # define the connection
    c = Connection(s, user='user_dn', password='user_password')
    c.bind()

    # perform the Modify operation
    c.modify('cn=user1,ou=users,o=company',
             {'givenName': [(MODIFY_REPLACE, ['givenname-1-replaced'])],
              'sn': [(MODIFY_REPLACE, ['sn-replaced'])]})
    print(c.result)

    # close the connection
    c.unbind()