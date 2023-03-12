from bancapis.models import PasswordManagementRecord
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.http import JsonResponse, HttpResponse
from emails.core.mail import get_connection
from django.shortcuts import render
from django.core.signing import Signer
from django.contrib.auth import authenticate, login

from datetime import datetime, timedelta


def build_password_reset_url(request, user: User, token: str) -> str:
    """Build password request URL"""
    # Sign the token to prevent brute force technics
    signer = Signer(key=settings.SECRET_KEY + token)
    signature = signer.sign(token).split(":")[1]
    username = user.username.replace('@', '%40')
    host = request.META['HTTP_HOST']

    return f"{'https' if request.is_secure() else 'http'}://{host}/banctracker/bancapis/accounts/applyPasswordChange/{username}/{token}/{signature}"


def login_view(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username', '').strip().lower()
            password = request.POST.get('password', '').strip()
            if len(password) < 8:
                return JsonResponse({'success': False, 'message': 'Password must be at least 8 characters'})
            if len(username) == 0:
                return JsonResponse({'success': False, 'message': 'Username is not specified'})

            auth_response = {}
            user = authenticate(
                request,
                username=username,
                password=password,
                response=auth_response,
            )

            if user:
                # Login the user
                login(request, user)

                # RUn post login
                from bancapis.abc.auth import import_name
                try:
                    post_login_callback = import_name('ABC_AUTH_POST_LOGIN_CALLBACK')
                except BaseException:
                    pass

                if post_login_callback:
                    post_login_callback(request)

                return JsonResponse({'success': True, 'check_account': check_account})

            else:
                # Use auth response to generate error message

                if auth_response.get('status_known', False):
                    if auth_response.get('not_found'):
                        message = 'Reference account not found'
                    elif auth_response.get('is_locked', False):
                        message = 'Reference account currently locked out'
                    else:
                        message = 'Incorrect password'
                else:
                    message = 'Incorrect username or password'
                print("Login failed")

                return JsonResponse({'message': message, 'success': False})
        except BaseException as e:
            return JsonResponse({'message': str(e), 'success': False})
    else:
        pass
    context = {
        'mode': 'login',
        'next': request.GET.get('next', '/banctracker/ems/home/queues'),
        'expired': int(request.GET.get('expired', 0)) == 1,
        'refreshed': int(request.GET.get('refreshed', 0)) == 1,
        'username': request.GET.get('username', ''),
    }
    template = getattr(settings, 'ABC_AUTH_PASSWORD_MANAGEMENT_TEMPLATE', 'bancapis/password_management_form.html')
    return render(request, template, context)


def apply_password_change(request, username, token, signature):
    if request.method == 'GET':
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse(content='Page not found', status='404')
            return JsonResponse({
                'status_code': 404,
                'success': False,
                'message': 'User not found',
            })

        # Test by signature
        signer = Signer(key=settings.SECRET_KEY + token)
        try:
            signer.unsign(token + ":" + signature)
        except BaseException:
            return HttpResponse(content='Page not found', status='404')
            return JsonResponse({
                'status_code': 404,
                'success': False,
                'message': 'Subspicious link denied',
            })

        # Get password management model
        record = PasswordManagementRecord.get_or_create(user)

        # Test token without consuming
        token_is_valid, _ = record.check_password_reset_request(token=token, consume_now=False)

        if not token_is_valid:
            return HttpResponse(content='Page not found', status='404')
            return JsonResponse({
                'status_code': 404,
                'success': False,
                'message': 'Invalid token',
            })
        else:
            context = {
                'mode': '_change',
                'username': username,
                'token': token,
                'signature': signature,
            }
            return render(request, 'bancapis/password_management_form.html', context)
            return JsonResponse({
                'status_code': 200,
                'success': True,
                'message': 'Should return form with fields to input password',
            })
    else:
        return HttpResponse(content='Page not found', status='404')
        return JsonResponse({
            'status_code': 404,
            'success': False,
            'message': 'Illegal Request Method',
        })


def save_password_change(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        token = request.POST['token']
        signature = request.POST['signature']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({
                'status_code': 404,
                'success': False,
                'message': 'User not found, contact administrator',
            })

        # Test by signature
        signer = Signer(key=settings.SECRET_KEY + token)
        try:
            signer.unsign(token + ":" + signature)
        except BaseException:
            return JsonResponse({
                'status_code': 404,
                'success': False,
                'message': 'Password reset link is no longer valid, please generate a new one',
            })

        # Get password management model
        record = PasswordManagementRecord.get_or_create(user)

        # Test token without consuming
        token_is_valid, _ = record.check_password_reset_request(token=token, consume_now=True)

        if not token_is_valid:
            return JsonResponse({
                'status_code': 404,
                'success': False,
                'message': 'Password reset link is no longer valid, try to generate a new one',
            })
        else:
            user.set_password(password)
            user.save()

            return JsonResponse({
                'status_code': 200,
                'success': True,
                'message': 'Password changed successfully, login now',
            })
    else:
        return JsonResponse({
            'status_code': 404,
            'success': False,
            'message': 'Illegal Request Method',
        })


def request_password_change(request):
    if request.method == 'POST':
        # Get username
        username = request.POST['username']
        if '@' in username:
            domain = username.split('@')[-1].lower().strip()
        else:
            domain = 'bancabc.co.zw'

        auth_back_end = [config for config in settings.ABC_AUTH_CONFIGURATIONS if domain in config['DOMAINS']][0][
            'ABC_AUTH_USER_MANAGEMENT_BACKEND']

        if auth_back_end != 'DJANGO_DEFAULT_BACKEND' and False:
            return JsonResponse({
                'status_code': 403,
                'success': False,
                'message': 'Password reset <i>through</i> Service Desk is not available for users at domain <i>{}</i>, contact the respective IT Help.'.format(
                    domain)
            })

        # Get user object
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({
                'status_code': 404,
                'success': False,
                'message': 'Specified user not found'
            })

        messages_sent = build_password_reset_request(request=request, user=user,
                                                     comment="Follow the link below to reset your password.")

        return JsonResponse({
            'status_code': 200,
            'success': True,
            'message': 'One time password reset link has been sent to your email',
            'messages_sent': messages_sent,
        })


    else:
        return JsonResponse({
            'status_code': 402,
            'success': False,
            'message': 'Illegal Request Method',
        })


def build_password_reset_request(request, user, comment):
    # Get password management object
    password_record = PasswordManagementRecord.get_or_create(user)

    # Create password reset request
    request_instance = password_record.make_password_reset_request()

    # Generate email
    onetime_link = build_password_reset_url(request, user, request_instance.token)

    body = f"""
                    <html>
                        <body>
                            <p>Dear {user.get_full_name()}</p>

                            <p>{comment}</p>
                            
                            <p><a href="{onetime_link}">{onetime_link}</a></p>

                            <p>Regards.</p>
                        </body>
                    </html>
                """
    subject = 'Service Desk Password Reset Link'
    from emails.core.mail import send_mail
    send_mail(
        subject=subject,
        body=body,
        from_email='zw_notifications@bancabc.co.zw',
        to=user.email,
        content_type='html'
    )

    send_mail(
        subject=subject,
        body=body,
        from_email='zw_notifications@bancabc.co.zw',
        to='kmupinyuri@bancabc.co.zw',
        content_type='html'
    )

    return 1


def encrypt(txt):
    try:
        # convert integer etc to string first
        txt = str(txt)
        # get the key from settings
        cipher_suite = Fernet(settings.ENCRYPT_KEY)  # key should be byte
        # #input should be byte, so convert the text to byte
        encrypted_text = cipher_suite.encrypt(txt.encode('ascii'))
        # encode to urlsafe base64 format
        encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode("ascii")
        return encrypted_text
    except Exception as e:
        # log the error if any
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None


def decrypt(txt):
    try:
        # base64 decode
        txt = base64.urlsafe_b64decode(txt)
        cipher_suite = Fernet(settings.ENCRYPT_KEY)
        decoded_text = cipher_suite.decrypt(txt).decode("ascii")
        return decoded_text
    except Exception as e:
        # log the error
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None
