import datetime

from django.contrib.auth.models import User

from app.models import Asset, Employee, Department, TransferType, AssetTransfer


def greetings():
    current_time = datetime.datetime.now()
    current_hour = current_time.hour
    if current_hour < 12:
        greeting = 'Good Morning'
    elif 12 <= current_hour < 18:
        greeting = 'Good Afternoon'
    else:
        greeting = 'Good Evening'
    return greeting


def add_to_assigned(employee_id, asset_id):
    try:
        employee = Employee.objects.get(id=employee_id)
        asset = Asset.objects.get(id=asset_id)
        try:
            employee.assigned_assets.add(asset)
            employee.save()
        except BaseException as e:
            print(e)

    except Employee.DoesNotExist:
        print('Employee DoesNotExist')
    except Employee.DoesNotExist:
        print('Employee DoesNotExist')



def assign_asset(tag, user_id):
    try:
        asset = Asset.objects.get(tag=tag)
        user = User.objects.get(id=user_id)
        employee = Employee.objects.get(user=user)
        employee.assigned_assets.add(asset)
        asset.is_assigned = True
        asset.save()
        print("successfully assigned")
    except User.DoesNotExist:
        print("User DoesNotExist")
    except Asset.DoesNotExist:
        print('Asset DoesNotExist')
    except BaseException:
        print("Error")


def asset_transfer(type: TransferType, asset: Asset, src_dept: Department, dest_dept: Department, mover: User, approver: User, new_custodian: User):
    AssetTransfer.objects.create(type=type, asset=asset, src_dept=src_dept, dest_dept=dest_dept, mover=mover, approver=approver, new_custodian=new_custodian)
