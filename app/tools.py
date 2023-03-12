import datetime
from smtplib import SMTPAuthenticationError, SMTPException

from django.contrib.auth.models import User
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from app.models import AssetTransfer, Asset, WorkBranch, Department, Employee, ExternalCompany, TransferType, \
    ReasonForTransfer, Application
from app.notifications import notify_asset_transfer
from bancapis.abc.auth import ADUserStore, get_setting
from core import settings


def generate_ref():
    from app.models import AssetTransfer
    url = "ABCTRANSFER{0:0>4}"

    temp_url = url.format(AssetTransfer.objects.all().count() + 1)
    return temp_url


def make_manager(username):
    try:
        user = User.objects.get(username=username)
        employee = Employee.objects.get(user=user)
        employee.is_manager = True
        employee.save()
        print(username, ' manager')

    except User.DoesNotExist:
        print("User not found")

    except Employee.DoesNotExist:
        print("Employee not found")


def make_procurer(username):
    try:

        user = User.objects.get(username=username)
        employee = Employee.objects.get(user=user)
        employee.is_procurer = True
        employee.save()
        print(username, "procurer")

    except User.DoesNotExist:
        print("User not found")

    except Employee.DoesNotExist:
        print("Employee not found")


def make_deployer(username):
    try:
        user = User.objects.get(username=username)
        employee = Employee.objects.get(user=user)
        employee.is_deployer = True
        employee.save()
        print(username, "deployer")
    except User.DoesNotExist:
        print("User not found")

    except Employee.DoesNotExist:
        print("Employee not found")


def remove_deployer(username):
    try:
        user = User.objects.get(username=username)
        employee = Employee.objects.get(user=user)
        employee.is_deployer = False
        employee.save()

    except User.DoesNotExist:
        print("User not found")

    except Employee.DoesNotExist:
        print("Employee not found")


def remove_procurer(username):
    try:

        user = User.objects.get(username=username)
        employee = Employee.objects.get(user=user)
        employee.is_procurer = False
        employee.save()
        print(username, "procurer")

    except User.DoesNotExist:
        print("User not found")

    except Employee.DoesNotExist:
        print("Employee not found")


def remove_manager(username):
    try:
        user = User.objects.get(username=username)
        employee = Employee.objects.get(user=user)
        employee.is_manager = False
        employee.save()

    except User.DoesNotExist:
        print("User not found")

    except Employee.DoesNotExist:
        print("Employee not found")


def unlock_asset(asset):
    asset.locked = False
    asset.on_repairs = False
    asset.save()


def get_asset_or_404(id):
    try:
        asset = Asset.objects.get(id=id)
        return asset
    except Asset.DoesNotExist:
        print("Asset not found")
        return None


def re_assign(self, user, asset):
    try:
        asset.custodian_user = User
        asset.save()
    except BaseException as e:
        print(e)


def notify_user(request, transfer, file_name):
    subject = "Asset Assignment"
    email_template_name = f"app/{file_name}"

    c = {
        "transfer": transfer,
        'domain': request.get_host(),
        'site_name': 'Asset Manager',
        'protocol': 'http',
    }
    email = render_to_string(email_template_name, c)
    try:
        if file_name == "approval_request.txt":
            send_mail(
                subject,
                email,
                settings.EMAIL_HOST_USER,
                [transfer.approved_by.email],
                fail_silently=False,
            )
            print("Email Sent")
        elif file_name == "notify_user.txt":
            send_mail(
                subject,
                email,
                settings.EMAIL_HOST_USER,
                [transfer.new_custodian.email],
                fail_silently=False,
            )
            print("Email Sent")

    except BadHeaderError:
        print("Failed")
        return HttpResponse('Invalid header found.')
    except SMTPAuthenticationError:
        print("Failed to authenticate")
    except SMTPException:
        print("Failed")


def lock_asset(asset):
    try:
        asset = Asset.objects.get(id=asset.id)
        asset.locked = True
        asset.save()
        print("locked now")
    except Asset.DoesNotExist:
        print("No Asset Match")
    except BaseException:
        print("Failed")


def is_locked(asset):
    if asset.locked:
        return asset.locked
    else:
        return asset.locked


def create_user(username=None, first_name=None, last_name=None, title=None, email_address=None, mobile_number=None,
                extension=None, work_address=None, department=None, sub_department=None, branch=None,
                profile_level='NORMAL'):
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
    employee = Employee.objects.create(
        user=new_user,
        title=title,
        mobile_number=mobile_number,
        extension=extension,
        department=department,
        sub_department=sub_department,
        branch=branch,
        work_address=work_address,
        profile_level=profile_level
    )

    return new_user, 0, 'User successfully created'


def create_user_from_attributes(attributes):
    """
        attributes - Attributes from active directory
        username,first_name,last_name,title,department,description
        mobile_number,extension,email_address,work_address
    """
    from bancapis.abc.auth import ADUserStore
    input_department = attributes.get('department', None)
    input_branch = attributes.get('branch', None)

    if input_department and not isinstance(input_department, Department):
        # Get departments
        departments = list(Department.objects.values_list('name', flat=True))
        # Predict department
        department_name = ADUserStore.predict_department(
            ad_department=attributes.get('department', None),
            ad_description=attributes.get('description', None),
            sys_departments=departments
        )
        if department_name:
            input_department = Department.objects.get(name=department_name)
        else:
            input_department = None
    if input_branch and not isinstance(input_branch, WorkBranch):
        # Get departments
        branches = list(WorkBranch.objects.values_list('name', flat=True))
        # Predict department
        branch_name = ADUserStore.predict_branch(
            ad_address=attributes.get('work_address', None),
            sys_branches=branches
        )
        if branch_name:
            input_branch = WorkBranch.objects.get(name=branch_name)
        else:
            input_branch = None
    # Create user
    user, code, message = create_user(
        username=attributes['username'].lower(),
        first_name=attributes['first_name'].capitalize(),
        last_name=attributes['last_name'].capitalize(),
        title=attributes.get('title', None),
        email_address=attributes.get('email_address', None),
        extension=attributes.get('extension', None),
        mobile_number=attributes.get('mobile_number', None),
        work_address=attributes.get('work_address', None),
        department=input_department,
        branch=input_branch,
        sub_department=attributes.get('sub_department', None)
    )

    print(user)

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


def calculate_lifespan(date_of_purchase):
    import datetime
    from dateutil.relativedelta import relativedelta
    now = datetime.datetime.now()

    difference = relativedelta(now, date_of_purchase)
    print("My years: " + str(difference.years))

    return str(difference.years)


def asset_drawback(id):
    try:
        asset = Asset.objects.get(id=id)
        if not asset.locked:
            transaction = Asset.objects.create()

    except Asset.DoesNotExist:
        print("Asset asset does not exist")

    except BaseException as exception:
        print(exception)


def return_from_repairs():
    pass


def add_to_department(asset: Asset, department: Department):
    try:
        department.departmental_assets.add(asset)
    except BaseException as e:
        print(e)


def assign_to_user(user: User, asset: Asset):
    try:
        asset.assigned_to = user
    except User.DoesNotExist:
        print("User does not exist")
    except Asset.DoesNotExist:
        print("Asset does not exist")


def acknowledge_custody(user: User, asset: Asset):
    try:
        asset.custodian_user = user
        add_to_department(asset, user.employee.department)

    except Asset.DoesNotExist:
        print("Asset not found")

    except User.DoesNotExist:
        print("user not found")

    finally:
        asset.save()
    print("Acknowledged")
    # Employee.objects.


def release_custody(user, asset):
    asset.custodian_user = None


def send_for_repairs(asset: Asset, company: ExternalCompany, approved_by: User, being_moved_by: User,
                     reason: ReasonForTransfer):
    try:
        transfer = AssetTransfer.objects.create(
            reference=generate_ref(),
            type=TransferType.objects.get(name="External"),
            asset=asset,
            company=company,
            being_moved_by=being_moved_by,
            approved_by=approved_by,
            external=True,
            new_custodian=None,
            reason_for_transfer=reason,
        )
        transfer.save()
        asset.on_repairs = True
        asset.save()
        notify_asset_transfer(transfer.id)
    except BaseException as e:
        print(e)


def assign_asset_to_usernames():
    from app.models import Asset
    from django.contrib.auth.models import User
    unassigned_assets = Asset.objects.filter(assigned_to=None)

    for asset in unassigned_assets:
        if asset.username is not None and asset.assigned_to is None:
            try:
                user = User.objects.get(username=asset.username)
                asset.assigned_to = user
                asset.custodian_user = user
                asset.is_assigned = True
                asset.allocated = True
                asset.save()
                print("Successfully done")
            except User.DoesNotExist:
                print("user does not exist")
            except Asset.DoesNotExist:
                print("Asset does not exist")
            except BaseException as exception:
                print(exception)
        else:
            print("No user name on asset")


def fully_set_up(asset):
    from app.models import Asset, Application
    applications = Application.objects.all()
    asset.installed_applications.add(applications)

def schedule_run():
    from datetime import datetime
    from threading import Timer

    x = datetime.today()
    y = x.replace(day=x.day + 1, hour=1, minute=0, second=0, microsecond=0)
    delta_t = y - x

    secs = delta_t.seconds + 1

    def hello_world():
        print("hello world")
        # ...

    from app.from_xl import use_existing_template
    t = Timer(secs, use_existing_template)
    t.start()

def start_redis_server():
    import redis
    print("hello")
    redis_host = "localhost"
    redis_port = 6379
    redis_password = ""
    # step 3: create the Redis Connection object
    try:
        # The decode_repsonses flag here directs the client to convert the responses from Redis into Python strings
        # using the default encoding utf-8.  This is client specific.
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

        # step 4: Set the hello message in Redis
        r.set("msg:hello", "Hello Redis!!!")

        # step 5: Retrieve the hello message from Redis
        msg = r.get("msg:hello")
        print(msg)

    except Exception as e:
        print(e)



