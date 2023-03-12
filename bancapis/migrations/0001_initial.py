# Generated by Django 4.1.1 on 2022-09-15 06:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordManagementRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bad_password_count', models.IntegerField(default=0)),
                ('password_change_required', models.BooleanField(default=True)),
                ('password_change_disabled', models.BooleanField(default=False)),
                ('password_expiry_date', models.DateTimeField(default=None, null=True)),
                ('password_recovery_email', models.CharField(default=None, max_length=128, null=True)),
                ('password_recovery_phone', models.CharField(default=None, max_length=32, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PasswordRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(default='', max_length=64, null=True)),
                ('expiry', models.DateTimeField(default=None, null=True)),
                ('operation', models.CharField(default='RESET', max_length=8)),
                ('consumed', models.BooleanField(default=False)),
                ('record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bancapis.passwordmanagementrecord')),
            ],
        ),
    ]
