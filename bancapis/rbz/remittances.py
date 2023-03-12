from django.conf import settings
import requests

# Define constants

# Actions
ADD = 'ADD'
READ = 'READ'
REVERSE = 'REVERSE'

# TRANSACTION TYPES
INBOUND = 'INBOUND'
OUTBOUND = 'OUTBOUND'

# Transfer mode
CASH = 'CASH'
MOBILE = 'MOBILE'

APIS_HOST = "https://api.bdctrs.jugaad.co.zw"

default_settings = {
    'RBZ_BDX_X_API_KEY': '$apr1$0xpiuy83$80wyJVeTrN/UhcZuPA7pX.',
    'RBZ_BDX_INBOUND_READ_API_URL': f"{APIS_HOST}/api/v1/inbound/read/",
    'RBZ_BDX_INBOUND_ADD_API_URL': f"{APIS_HOST}/api/v1/inbound/add",
    'RBZ_BDX_INBOUND_REVERSE_API_URL': f"{APIS_HOST}/api/v1/inbound/reserve/",
    'RBZ_BDX_OUTBOUND_READ_API_URL': f"{APIS_HOST}/api/v1/inbound/read/",
    'RBZ_BDX_OUTBOUND_ADD_API_URL': f"{APIS_HOST}/api/v1/inbound/add",
    'RBZ_BDX_OUTBOUND_REVERSE_API_URL': f"{APIS_HOST}/api/v1/inbound/reverse/",
    'RBZ_BDX_EXCEPTION_DUPLICATE_ERROR': 'org.springframework.dao.DataIntegrityViolationException',
    'RBZ_BDX_API_USERNAME': 'munashe',
    'RBX_BDX_API_PASSWORD': ''
}


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


DUPLICATION_ERROR_EXCEPTION = get_setting('RBZ_BDX_EXCEPTION_DUPLICATE_ERROR')


def perform_action(action=None, transaction_type=None, body=None, reference=None, trials=None):
    """
        Invoke RESTFul call to RBZ remmitances controller
        Args:
            action              - Action to excuted  [String - ADD, READ, REVERSE]
            transaction_type    - Direction of transaction [String - INBOUND, OUTBOUND]
            body                - JSON describe the request body [Dictionary]
            reference           - ID or orignal reference for a transaction
    """
    if action == ADD:
        response = perform_action_add(request_body=body, transaction_type=transaction_type, trials=trials)
        return response
    else:
        raise RuntimeError(f'Action "{action}" not implemented')


def check_transaction_type(transaction_type, raise_error=False):
    assert isinstance(transaction_type, str), 'Transaction type must be of a string'
    transaction_type = transaction_type.strip().upper()
    if transaction_type in [INBOUND, OUTBOUND]:
        return transaction_type
    else:
        if raise_error:
            assert False, f'Invalid transaction type: {transaction_type}'
        else:
            return None


def perform_action_add(request_body, transaction_type=None, trials=None):
    # Ensure request is not none
    assert request_body is not None, 'Request body cannot be null'
    # Ensure request transaction type is valid
    transaction_type = check_transaction_type(transaction_type, raise_error=True)
    # Get API URL
    if transaction_type == INBOUND:
        api_url = get_setting('RBZ_BDX_INBOUND_ADD_API_URL')
    else:
        api_url = get_setting('RBZ_BDX_OUTBOUND_ADD_API_URL')

    # Get API KEY
    api_key = get_setting('RBZ_BDX_X_API_KEY')

    # Pack headers
    headers = {
        'Content-type': 'application/json',
        'x-api-key': api_key,
    }

    # Make RESTFul call
    try:
        response = requests.post(
            api_url,
            json=request_body,
            headers=headers,
        )
    except BaseException as e:
        # Mark as connection error
        return {
            "status_code": 501,
            "success": False,
            "message": "Request to RBZ failed due to connection error",
            "errors": [
                {'error_code': 501, 'error_msg': 'Request to RBZ failed due to connection error', 'error_obj': str(e)}
            ],
            "response_body": None
        }

    # Compile custom response
    if response.status_code == 200:
        return {
            'status_code': 200,
            'success': True,
            'message': 'Add operation completed successfully',
            'response_body': response.json()
        }

    elif response.status_code == 400:
        packed_response = {
            'status_code': 400,
            'success': False,
            'message': 'Base request or duplicate transaction reference',
            'errors': [],
            'response_body': None,
        }

        if bool(response.content) and response.json()[
            'exception'].lower().strip() == 'org.springframework.dao.dataintegrityviolationexception':
            packed_response['errors'].append({
                'error_code': 400,
                'error_msg': 'Original reference must by unique',
                'error_obj': 'org.springframework.dao.DataIntegrityViolationException',
                'response_body': None,
            })
        else:
            packed_response['errors'].append({
                'error_code': 400,
                'error_msg': 'Request body is malformed, missing attributes or invalid values',
                'error_obj': None,
                'response_body': None,
            })

        return packed_response

    elif response.status_code == 401:
        return {
            'status_code': 401,
            'success': False,
            'message': 'Access denined. Authorization required.',
            'errors': [{'error_code': 401, 'error_msg': 'Unauthorized', 'error_obj': None}],
            'response_body': None,
        }

    else:
        return {
            'status_code': 0,
            'success': False,
            'message': 'Base request or duplicate transaction reference',
            'errors': [{'error_code': 0, 'error_msg': 'Unknown exception', 'error_obj': None}],
            'response_body': None,
        }


def perform_action_reverse():
    pass


def perform_action_read():
    pass
