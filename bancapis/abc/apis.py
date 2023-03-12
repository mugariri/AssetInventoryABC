import json
from random import randint

import requests
from django.conf import settings


def get_setting(key):
    try:
        return getattr(settings, key)
    except AttributeError as e:
        if default_settings is None:
            raise AttributeError(f'Setting "{key}" is not defined in settings.py')
        try:
            return default_settings[key]
        except KeyError:
            raise AttributeError(f'Setting "{key}" is not defined in settings.py')


default_settings = {
    'ABC_API_HOST': 'http://10.120.3.60:25183/',  # DEFAULT TO UAT APIs
    'ABC_API_GET_TOKEN': 'api/GetToken',
    'ABC_API_SMS_SEND_SINGLE': 'api/SmsSendSingle',
    'ABC_API_GET_CUSTOMER_DETAILS_BY_CIF': 'api/FcubsGetUserDetailsByCIFOrAcc',
    'ABC_API_ACTIVE_DIRECTORY_AUTH': 'api/ActiveDirecoryAuthAsync',
    'ABC_AUTH_DOMAIN_QUALIFIED_NAME': 'abc.zw',
}


def build_api_url(api_name):
    return f"{get_setting('ABC_API_HOST')}{get_setting(api_name)}"


def get_token():
    banc_auth = requests.auth.HTTPBasicAuth(
        get_setting('ABC_AUTH_API_USERNAME'),
        get_setting('ABC_AUTH_API_PASSWORD'),
    )
    response = requests.get(build_api_url('ABC_API_GET_TOKEN'), auth=banc_auth)
    # print("GET_TOCKEN response..\n",response.json())
    banc_token = response.json()['bancabc_reponse']['value']

    return banc_token


def get_api_url(api_name, banc_token=None):
    if not banc_token:
        banc_token = get_token()
    banc_api = build_api_url(api_name)
    banc_api_url = f'{banc_api}?token={banc_token}'
    return banc_api_url


def send_notification(subject, message, receiver, url_api=None, trials=10):
    """
        Send notification: sender = zw_notications
    """
    count = 0
    while True:
        try:
            print("Send notification to:" + receiver)
            if not url_api:
                url_api = get_api_url('ABC_API_SMS_SEND_SINGLE')

            # Compile request body
            headers = {'Content-type': 'application/json'}
            payload = {
                "username": "bancabc",
                "mailTo": receiver,
                "mailCc": "",
                "mailBcc": "",
                "subject": subject,
                "message": message,
                "incTemplate": "",
                "templateNo": "2",
                "attachments": ""
            }
            response = requests.post(url_api, json=payload, headers=headers)
            print(response.json())
            break
        except BaseException as e:
            if (count < trials):
                count += 1
                continue
            break


def send_sms(phone_number: str, message: str, url_api=None):
    try:
        if not url_api:
            url_api = get_api_url(BANC_API_SMS_SEND_SINGLE)

        headers = {'Content-type': 'application/json'}
        payload = {
            "originator": get_setting('ABC_API_SMS_SOURCE'),
            "destination": phone_number,
            "messageText": message,
            "messageReference": "REF{}".format(randint(100000, 999999))
        }
        response = requests.post(url_api, json=payload, headers=headers)
        print("SMS_SEND_SINGLE response..", response.json())
        print(response.json())
        # return response.json()['bancabc_reponse']
        return {"success": True, "message": "Sms send succesifully"}
    except requests.exceptions.ConnectionError as e:
        return {"success": False, "message": "Failed to connnect to SMS server", "errorcode": "connection error"}
    except BaseException as e:
        raise  # @TODO Enter logs, but for null raise exception
        # @TODO Launch celery task to retry after 5 minutes, if retries reach 6 times, save to database
        # @Celery beat will do batch job, esecuting failed messaged
        # @TODO save as failed sms to database, which will be executed by celery
        return None


def send_email(username, mailTo, subject, message):
    payload = {
        "username": username,
        "mailTo": mailTo,
        "subject": subject,
        "message": "sample string 6",
        "incTemplate": False,
        "templateNo": "sample string 8"
    }
    try:
        url_api = get_api_url(BANC_API_ZW_NOTIFICATIONS)
        headers = {'Content-type': 'application/json'}
        response = requests.post(url_api, json=payload, headers=headers)
        print("SEND_EMAIL_API response..", response.json())
        print(response.json())
        return response.json()['bancabc_reponse']
    except BaseException as e:
        raise  # @TODO Enter logs, but for null raise exception
        # @TODO Launch celery task to retry after 5 minutes, if retries reach 6 times, save to database
        # @Celery beat will do batch job, esecuting failed messaged
        # @TODO save as failed sms to database, which will be executed by celery
        return None


def ldap_quick_athenticate_user(username, password):
    username = username.strip()
    password = password.strip()
    if username == "":
        raise ValueError("Username must not be empty")
    if username == "":
        raise ValueError("Password must not be empty")
    payload = {
        "username": username,
        "password": password,
        "domain": get_setting('ABC_AUTH_DOMAIN_QUALIFIED_NAME')
    }
    try:
        from datetime import datetime
        start = datetime.now()
        url_api = get_api_url('ABC_API_ACTIVE_DIRECTORY_AUTH')
        headers = {'Content-type': 'application/json'}
        response = requests.post(url_api, json=payload, headers=headers)
        print("ABC_API_ACTIVE_DIRECTORY_AUTH response..\n", response.json())
        response = response.json()['bancabc_reponse']
        end = datetime.now()
        print(f'Authentication completed in {(end - start).total_seconds()} seconds')
        return response['message'].strip() == 'success' and response['value']
    except BaseException as e:
        raise  # @TODO Enter logs, but for null raise exception
        # @TODO Launch celery task to retry after 5 minutes, if retries reach 6 times, save to database
        # @Celery beat will do batch job, esecuting failed messaged
        # @TODO save as failed sms to database, which will be executed by celery
        return None


def get_customer_info(cif):
    if cif is None:
        raise ValueError("Account CIF cannot be NoneType")
    cif = cif.strip()
    if not cif.isnumeric() or len(cif) < 7:
        raise ValueError("Account CIF must be 7 digits or at least 7 digits")
    url_api = get_api_url('ABC_API_GET_CUSTOMER_DETAILS_BY_CIF')
    url_api = f'{url_api}&accCif={cif[:7]}'
    headers = {'Content-type': 'application/json'}
    response = requests.post(url_api, headers=headers)
    return response.json()['bancabc_reponse']


def customer_info(cif):
    print('Query account:{}'.format(cif))
    response = get_customer_info(str(cif))
    accounts = []
    # print("--------------------------------------")
    for acc in response['value']:
        details = {
            'branch_code': acc[0],
            'first_name': acc[5],
            'last_name': acc[6],
            'account_number': acc[1],
            'phone_number': acc[10],
            'phone_number2': acc[11],
            'email_address': acc[16],
            'national_id': acc[9],
            'street': '{}\n{}\n{}'.format(*acc[13:16])
        }
        accounts.append(details)
    return accounts
