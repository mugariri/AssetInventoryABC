from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    can_clear = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class Software(models.Model):
    name = models.CharField(max_length=255)


class Computer(models.Model):
    abc_asset_tag = models.CharField(max_length=255, null=False, blank=True)
    new_active_directory_name = models.CharField(max_length=255, null=False, blank=True)
    old_active_directory_name = models.CharField(max_length=255, null=False, blank=True)
    configured_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE,
                                      related_name='configurations')
    custodian = models.TextField(max_length=255, null=True, blank=True)
    # software_installed = models.ManyToManyField(Software, null=True, blank=True)
    date_configured = models.DateTimeField(auto_now_add=True, blank=True)
    cleared = models.BooleanField(default=False, blank=True)
    date_cleared = models.DateTimeField(null=True, blank=True)
    cleared_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='clearings')

    def __str__(self):
        return f'{self.new_active_directory_name}'
