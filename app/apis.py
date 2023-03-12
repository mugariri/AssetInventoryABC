import json
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
    print(banc_token)
    return banc_token


def get_api_url(api_name, banc_token=None):
    if not banc_token:
        banc_token = get_token()
    banc_api = build_api_url(api_name)
    banc_api_url = f'{banc_api}?token={banc_token}'
    return banc_api_url


def send_notification(subject, message, receiver, url_api=None, trials=100):
    """
        Send notification: sender = zw_notications
    """
    # print(get_api_url('ABC_API_EMAIL_SEND_SINGLE'))
    # print(get_token())
    count = 0
    while True:
        try:
            print("Send notification to:" + receiver)
            if not url_api:
                url_api = get_api_url('ABC_API_EMAIL_SEND_SINGLE')
            # Compile request body
            headers = {'Content-type': 'application/json'}
            payload = {
                "mailTo": receiver,
                "mailCc": "",
                "mailBcc": "",
                "subject": subject,
                "incTemplate": True,
                "message": message,
                "templateNo": 2
            }
            response = requests.post(url_api, json=payload, headers=headers)
            print(response.json())
            return response.json()
            break
        except BaseException as e:
            if (count < trials):
                count += 1
                continue
            break
