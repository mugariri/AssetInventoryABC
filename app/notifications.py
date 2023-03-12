from threading import Thread
from time import sleep

from django.contrib.auth.models import User
from django.urls import reverse

from app.apis import send_notification
from app.models import AssetTransfer, HardwareRequisition, Employee
from app.utilities import greetings
from core.settings import PROTOCOL, HOST, PORT


#
# def notify_assignment(transfer: AssetTransfer):
#     dictionary = {
#         "subject": "Asset Assignment",
#         "message": f""" {greetings} {transfer.new_custodian.first_name} {transfer.new_custodian.last_name}
#
#             You have been assigned an asset {transfer.asset} by {transfer.being_moved_by.first_name} {transfer.being_moved_by.last_name}
#
#         """,
#         "receiver": "dmugariri@bancabc.co.zw",
#
#     }
#     thread = Thread(target=send_notification, kwargs=dictionary)
#     thread.start()
#     thread.join()
#
#
# def notify_pending_approval(transfer: AssetTransfer):
#     protocol = PROTOCOL
#     domain = '127.0.0.1'
#     port = 8000
#     dictionary = {
#         "subject": "Asset Assignment",
#         "message": f"""
#         {greetings} {transfer.approved_by.first_name} {transfer.approved_by.last_name}
#
#             An asset transfer has been intiated for {transfer.asset} by {transfer.being_moved_by.first_name} {transfer.being_moved_by.last_name}
#             requesting your approval kindly follow the link below to authorize
#
#             "<li>{protocol}://{domain}:{port}/{reverse('abcassetsmanager:asset_transfer' ,kwargs={'id':'1'})}</li>
#
#         """,
#         "receiver": "dmugariri@bancabc.co.zw",
#
#     }
#     thread = Thread(target=send_notification, kwargs=dictionary)
#     thread.start()
#     thread.join()
#
#


def notify_pending_approval(transfer_id):
    try:
        transfer = AssetTransfer.objects.get(id=transfer_id)
        # print(reverse('abcassetsmanager:asset_transfer', kwargs={'id':f'{transfer_id}' }))
        message = f"""
        Regards {transfer.approved_by.first_name} {transfer.approved_by.last_name}<br/><br/>
        Awaiting approval
        <br/><br/>
        <b>Asset Transfer Details</b>:<br/>
        
        AGENT : {transfer.being_moved_by.first_name} {transfer.being_moved_by.last_name}<br/><br/>
        
        RECEIPIENT : {transfer.new_custodian.first_name} {transfer.new_custodian.last_name}<br/><br/>
        
        ASSET TAG: {transfer.asset.tag}<br/><br/>
        
        SERIAL TAG: {transfer.asset.serial_tag}<br/><br/>
        
        REASON : {transfer.reason_for_transfer}<br/><br/>
        
        follow link below to action above transfer:<br/><br/>
 
        {PROTOCOL}://{HOST}:{PORT}/{reverse('abcassetsmanager:asset_transfer', kwargs={'id': f'{transfer_id}'})}
        
        
        """
        dictionary = {
            "subject": "Awaiting Approval",
            "message": message,
            "receiver": transfer.approved_by.email
        }
        Thread(target=send_notification, kwargs=dictionary).start()
        # thread
        # thread.join()
        # send_notification(subject="Awaiting Approval", message=message, receiver=transfer.new_custodian.email)
    except AssetTransfer.DoesNotExist:
        pass

    except BaseException as e:
        print(e)


def notify_asset_transfer(transfer_id):
    try:

        transfer = AssetTransfer.objects.get(id=transfer_id)

        message = f"""
        Regards  {transfer.new_custodian.first_name} {transfer.new_custodian.last_name}<br/>
        
        <br/><br/>
        <b>Asset Transfer Details</b>:<br/>

        AGENT : {transfer.being_moved_by.first_name} {transfer.being_moved_by.last_name}<br/><br/>

        RECEIPIENTS : {transfer.new_custodian.first_name} {transfer.new_custodian.last_name}<br/><br/>

        ASSET TAG: {transfer.asset.tag}<br/><br/>

        SERIAL TAG: {transfer.asset.serial_tag}<br/><br/>

        DEVICE TYPE : {transfer.asset.category}<br/><br/>
        
        REASON : {transfer.reason_for_transfer}<br/><br/>

        follow link below to acknowledge above transfer on recieving asset :<br/><br/>

        {PROTOCOL}://{HOST}:{PORT}{reverse('abcassetsmanager:acknowledge', kwargs={'id': f'{transfer_id}'})}

        """
        dictionary = {
            "subject": "Awaiting Acknowledgement",
            "message": message,
            "receiver": transfer.new_custodian.email
        }
        Thread(target=send_notification, kwargs=dictionary).start()
    except AssetTransfer.DoesNotExist:
        print("Transfer does not exist")
    except BaseException as e:
        print(e)
    pass


def notify_external_asset_transfer(transfer_id):
    try:
        transfer = AssetTransfer.objects.get(id=transfer_id)
        message = f"""
        <p> REGARDS {transfer.approved_by.first_name} {transfer.approved_by.last_name}</p>
        
        follow link below to authorize a transfer assigned to you :<br/><br/>

        <a href="{PROTOCOL}://{HOST}:{PORT}{reverse('abcassetsmanager:acknowledge', kwargs={'id': f'{transfer_id}'})}">Click Here To Action</a>

        """
        print(message, "Message")
        dictionary = {
            "subject": "External Transfer",
            "message": message,
            "receiver": transfer.approved_by.email,
        }
        Thread(target=send_notification, kwargs=dictionary).start()
    except AssetTransfer.DoesNotExist:
        print("Transfer does not exist")
    except BaseException as e:
        print(e)
    pass


def notify_hardware_request(id):
    try:
        hardware_request = HardwareRequisition.objects.get(id=id)
        message = f"""
            A Hardware Request requires your action kindly follow link below:<br/><br/>
            <a href="{PROTOCOL}://{HOST}:{PORT}{reverse('abcassetsmanager:approve_hardware_request', kwargs={'id': f'{id}'})}">Link</a>
        """
        dictionary = {
            "subject": "HEAD OF DEPARTMENT APPROVAL REQUEST",
            "message": message,
            "receiver": hardware_request.authorized_by.email
        }
        Thread(target=send_notification, kwargs=dictionary).start()
    except HardwareRequisition.DoesNotExist:
        print("Hardware Requisition does not exist")
    except BaseException as e:
        print(e)
    pass


def in_manager_notify_hardware_request(id):
    try:
        hardware_request = HardwareRequisition.objects.get(id=id)
        message = f"""
            A Hardware Request requires your action kindly follow link below:<br/><br/>
            <a href='{PROTOCOL}://{HOST}:{PORT}/{reverse('abcassetsmanager:infrastructure_manager_approve', kwargs={'id': f'{id}'})}'>Link</a>
        """
        for employee in Employee.objects.filter(IN_manager=True):

            try:
                dictionary = {
                    "subject": "INFRASTRUCTURE MANAGER APPROVAL REQUEST",
                    "message": message,
                    "receiver": employee.user.email
                }
                Thread(target=send_notification, kwargs=dictionary).start()
            except BaseException as exception:
                print(exception)
    except HardwareRequisition.DoesNotExist:
        print("Hardware Requisition does not exist")
    except BaseException as e:
        print(e)
    pass


def head_of_tech_notify_hardware_request(id):
    try:
        hardware_request = HardwareRequisition.objects.get(id=id)
        message = f"""
            A Hardware Request requires your action kindly follow link below:<br/><br/>
            <a href="{PROTOCOL}://{HOST}:{PORT}/{reverse('abcassetsmanager:head_of_tech_services_approve', kwargs={'id': f'{id}'})}">Follow Link To Action</a>
        """
        for employee in Employee.objects.filter(is_head_of_tech=True):
            dictionary = {
                "subject": "HEAD OF TECHNOLOGY SERVICES APPROVAL REQUEST",
                "message": message,
                "receiver": employee.user.email
            }
            Thread(target=send_notification, kwargs=dictionary).start()
    except HardwareRequisition.DoesNotExist:
        print("Hardware Requisition does not exist")
    except BaseException as e:
        print(e)
    pass


def line_manager_notify_hardware_request(id):
    try:
        hardware_request = HardwareRequisition.objects.get(id=id)
        message = f"""
            A Hardware Request requires your action kindly follow link below:<br/><br/>
            <a href="{PROTOCOL}://{HOST}:{PORT}/{reverse('abcassetsmanager:line_manager_approve', kwargs={'id': f'{id}'})}">Link</a>
        """
        dictionary = {
            "subject": "LINE MANAGER REQUEST",
            "message": message,
            "receiver": hardware_request.requisitioner.employee.line_manager.email,
        }
        Thread(target=send_notification, kwargs=dictionary).start()
    except HardwareRequisition.DoesNotExist:
        print("Hardware Requisition does not exist")
    except BaseException as e:
        print(e)
    pass
