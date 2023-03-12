from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from django.core.mail import BadHeaderError, send_mail
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from core import settings


def password_reset_request(request):
    if request.method == "POST":
        email_address = request.POST.get('email')
        associated_users = User.objects.filter(Q(email=email_address))
        if associated_users.exists():
            for user in associated_users:
                subject = "Password Reset Requested"
                email_template_name = "password/password_reset_email.txt"
                c = {
                    "email": user.email,
                    'domain': '127.0.0.1:8000',
                    'site_name': 'Website',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                }
                email = render_to_string(email_template_name, c)
                try:
                    send_mail(
                        subject,
                        email,
                        settings.DEFAULT_FROM_EMAIL,
                        [email_address],
                        fail_silently=False
                    )

                except BadHeaderError:

                    return HttpResponse('Invalid header found.')

                messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
                return redirect("app:password_reset_done")
            messages.error(request, 'An invalid email has been entered.')

    return render(request=request, template_name="password/password_reset.html",
                  context={})
