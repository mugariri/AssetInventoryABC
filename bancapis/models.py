from datetime import timedelta, datetime
from uuid import uuid4

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import models
from django.contrib.auth.models import User  # Create your models here.


class PasswordManagementRecord(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bad_password_count = models.IntegerField(default=0)
    password_change_required = models.BooleanField(default=True)
    password_change_disabled = models.BooleanField(default=False)
    password_expiry_date = models.DateTimeField(default=None, null=True)
    password_recovery_email = models.CharField(default=None, null=True, max_length=128)
    password_recovery_phone = models.CharField(default=None, null=True, max_length=32)

    def make_password_reset_request(self):
        # Instantiate token generate
        token = PasswordResetTokenGenerator().make_token(self.user)

        # TODO Disable existing ones

        # Create password reset instance
        reset_request = PasswordRequest.objects.create(
            operation=PasswordRequest.RESET,  # TODO also add time stamp
            record=self,
            token=token,
            expiry=datetime.now() + timedelta(hours=24),
            consumed=False,
        )

        # Set password record to require password change
        PasswordManagementRecord.objects.filter(pk=self.pk).update(password_change_required=True)

        return reset_request

    def check_password_reset_request(self, token, consume_now=False):
        """
            Validates the password reset request and consume the request if it is valid
            and consume_now is set to True

            Returns (Validity State, Consumed State)
        """
        check_queryset = PasswordRequest.objects.filter(record=self, token=token, consumed=False)
        # When the token is invalid (Either expired, already used or doesn't exist)
        if check_queryset.exists():
            # Consume if consume_now is True
            if consume_now:
                # Automatically clears other old tokens
                check_queryset.update(consumed=True)
                PasswordManagementRecord.objects.filter(pk=self.pk).update(bad_password_count=0)
                response = (True, True)
            else:
                response = (True, False)
        else:
            response = (False, False)  #

        return response  # Tuple of (Validity State, Consumed State)

    @staticmethod
    def get_or_create(key) -> 'PasswordManagementRecord':
        if isinstance(key, int) or isinstance(key, str):
            query = {"user__pk": key}
        elif isinstance(key, User):
            query = {"user__pk": key.pk}
        else:
            raise ValueError("Invalid query key type -'{}'".format(type(key)))

        try:
            management_record = PasswordManagementRecord.objects.get(**query)
        except PasswordManagementRecord.DoesNotExist:
            if isinstance(key, int) or isinstance(key, str):
                key = User.objects.get(key=key)
            management_record = PasswordManagementRecord.objects.create(
                user=key,
                password_change_required=True,
                password_change_disabled=False,  # TODO Set from settings
                password_expiry_date=None,  # TODO Set from settings
                password_recovery_email=None,
                password_recovery_phone=None,  # Default to other mechanisms
            )

        return management_record


class PasswordRequest(models.Model):
    RESET = 'RESET'
    UNLOCK = 'UNLOCK'
    record = models.ForeignKey(PasswordManagementRecord, on_delete=models.CASCADE)
    token = models.CharField(default="", null=True, max_length=64)
    expiry = models.DateTimeField(default=None, null=True)
    operation = models.CharField(default=RESET, max_length=8)
    consumed = models.BooleanField(default=False)


def test_api():
    PasswordRequest.objects.all().delete()

    user = User.objects.get(username='kmupinyuri')

    record = PasswordManagementRecord.get_or_create(user)

    request = record.make_password_reset_request()
    print("Test 1: With consume")
    print(record.passwordrequest_set.all().values('token', 'consumed'))
    print("Test 1: After check no consume")
    record.check_password_reset_request(token=request.token)
    print(record.passwordrequest_set.all().values('token', 'consumed'))

    request = record.make_password_reset_request()
    print("Test 2: With consume")
    print(record.passwordrequest_set.all().values('token', 'consumed'))
    print("Test 2: After check no consume")
    record.check_password_reset_request(token=request.token, consume_now=True)
    print(record.passwordrequest_set.all().values('token', 'consumed'))
