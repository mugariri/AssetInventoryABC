import datetime

import pytz
from django.contrib.auth.models import User, Group
from django.db import models
import django.utils.timezone as djtimezone

# Create your models here.
from django.db.models.fields import related
from django.utils.html import format_html
from django_celery_beat.models import ClockedSchedule
from core import settings


class Department(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    head = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=255)
    date_created = models.DateTimeField(default=djtimezone.now)
    departmental_assets = models.ManyToManyField('Asset', blank=True)

    class Meta:
        managed = True
        db_table = 'department'
        ordering = ['name', ]

    def __str__(self):
        return self.name


class Employee(models.Model):
    PROFILE_CHOICES = (
        ('VIP', 'VIP'),
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low')
    )
    employee_number = models.CharField(max_length=255, blank=True, null=True)
    work_address = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    mobile_number = models.CharField(max_length=255, null=True, blank=True)
    work_branch = models.CharField(max_length=255, null=True, blank=True)  #
    branch = models.ForeignKey('WorkBranch', on_delete=models.SET_NULL, null=True, blank=True)
    extension = models.CharField(max_length=255, null=True, blank=True)
    user = models.OneToOneField(User, unique=True, blank=True, on_delete=models.CASCADE, primary_key=True)
    department = models.ForeignKey(Department, db_column="department_id", blank=True, null=True,
                                   on_delete=models.CASCADE)
    id_deployer = models.BooleanField(default=False)
    sub_department = models.ForeignKey('SubDepartment', null=True, blank=True, on_delete=models.SET_NULL)
    profile_level = models.CharField(max_length=255, choices=PROFILE_CHOICES, null=False, default='NORMAL', blank=True)
    line_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_leader')
    is_authorized = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_procurer = models.BooleanField(default=False)
    is_deployer = models.BooleanField(default=False)
    assigned_assets = models.ManyToManyField('Asset', blank=True, )
    updated = models.BooleanField(default=False)
    is_head_of_dept = models.BooleanField(default=False)
    IN_manager = models.BooleanField(default=False)
    is_head_of_tech = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        managed = True
        db_table = 'employee'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        permissions = (
            ('can_create_company', 'can create company'),
            ('can_delete_company', 'can delete company'),
            ('can_update_company', 'can update company'),
            ('can_give_rights', 'can give rights')
        )


class AssetPool(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    assets = models.ManyToManyField('Asset')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class WorkBranch(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=4, null=True, blank=True, unique=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    default_extension = models.CharField(max_length=80, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Branches'

    def __str__(self):
        return self.name


class Customer(models.Model):
    email_address = models.CharField(max_length=70)
    phone_number = models.CharField(max_length=90)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    source = models.CharField(max_length=255)
    userid = models.CharField(max_length=80)
    branch = models.CharField(max_length=50)
    brn = models.CharField(max_length=50)
    account_number = models.CharField(max_length=25, blank=True, null=True)
    card_number = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'customer'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'


class SubDepartment(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=255, null=True)
    date_created = models.DateTimeField(default=djtimezone.now)

    class Meta:
        managed = True
        verbose_name_plural = 'Sub Departments'

    def __str__(self):
        return self.name


class AssetClass(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Asset Class'
        verbose_name_plural = 'Asset Classes'


class AssetCategory(models.Model):
    asset_class = models.ForeignKey(AssetClass, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, unique=True)
    date_created = models.DateTimeField(default=djtimezone.now)
    life_span_in_years = models.IntegerField(null=True, blank=True)
    department_in_charge = models.ForeignKey(Department, db_column="department_id", blank=True, null=True,
                                             on_delete=models.CASCADE)
    sub_department = models.ForeignKey(SubDepartment, db_column="sub_department_id", blank=True, null=True,
                                       on_delete=models.SET_NULL, related_name='child_department')

    @staticmethod
    def get_or_create(name):
        try:
            x = AssetCategory.objects.get(name__iexact=name)
            return (False, x)
        except BaseException:
            x = AssetCategory.objects.create(name=name)
            x.save()
            return (True, x)

    class Meta:
        managed = True
        db_table = 'asset_category'
        verbose_name = 'Asset Category'
        verbose_name_plural = 'Asset Categories'
        ordering = ['name', ]

    def __str__(self):
        return self.name


CURRENCY = (
    ('USD', 'USD'),
    ('EUR', 'EUR'),
    ('GBP', 'GBP'),
    ('ZWL', 'ZWL'),
    ('ZAR', 'ZAR'),
)

GENERAL_LEDGERS = (
    ('AL8373', 'AL8373'),
    ('AL8374', 'AL8374'),
    ('AL8375', 'AL8375'),
)


class General_Ledger(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    account = models.CharField(max_length=255, unique=True, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Asset(models.Model):
    # installed_applications = models.ManyToManyField('Application', blank=True)
    active_directory_id = models.CharField(max_length=255, null=True, blank=True)
    category = models.ForeignKey(AssetCategory, null=True, blank=True, on_delete=models.CASCADE)
    tag = models.CharField(max_length=255, unique=True, null=False)
    serial_tag = models.CharField(max_length=255, null=False, unique=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    colour = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    custodian_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='AssignedTo')
    date_created = models.DateTimeField(default=djtimezone.now)
    purchase_date = models.DateTimeField(null=True, blank=True)
    received_date = models.DateTimeField(null=True, blank=True, default=djtimezone.now)
    allocated_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='allocated')
    purchase_request_document = models.FileField(null=True, blank=True, upload_to='hardware requests')
    allocated = models.BooleanField(default=False)
    is_assigned = models.BooleanField(default=False)
    specs = models.ForeignKey('Specification', on_delete=models.SET_NULL, null=True, blank=True)
    deployment_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deployment_by', null=True,
                                      blank=True)
    external_custodian = models.ForeignKey('ExternalCompany', on_delete=models.SET_NULL, null=True, blank=True)
    registered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registered_by', null=True,
                                      )
    allocated_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    person_name = models.CharField(max_length=100, null=True, blank=True)
    location = models.ForeignKey(WorkBranch, on_delete=models.SET_NULL, null=True, blank=True)
    registration_number = models.CharField(max_length=20, null=True, unique=True, blank=True)
    location = models.ForeignKey(WorkBranch, null=True, blank=True, on_delete=models.RESTRICT)
    held_in = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    model = models.CharField(max_length=255, null=True, blank=True)
    specs = models.CharField(max_length=255, null=True, blank=True)
    year_of_purchase = models.DateField(null=True, blank=True)
    on_repairs = models.BooleanField(default=False)
    date_of_manufacturing = models.DateField(null=True, blank=True)
    product_id = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    bios_date = models.CharField(max_length=10, null=True, blank=True)
    obsolete = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True, choices=CURRENCY)
    general_ledger_account = models.ForeignKey(General_Ledger, blank=True, null=True, on_delete=models.SET_NULL)


    def validate_assignment(self):
        if self.assigned_to is None:
            self.is_assigned = False

    class Meta:
        managed = True
        db_table = 'asset'
        ordering = ('-date_created','-tag',)
        permissions = (
            ("can_create_asset", "Can Create Asset"),
        )

    def __str__(self):
        return self.tag


class TransferType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class ReasonForTransfer(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name


class AssetTransfer(models.Model):
    reason_for_transfer = models.CharField(max_length=255, null=True, blank=True)
    external = models.BooleanField(default=False)
    reference = models.CharField(max_length=255, null=True, blank=True)
    type = models.ForeignKey(TransferType, on_delete=models.CASCADE, null=True, blank=True)  # internal or external
    multiple_assets = models.ManyToManyField(Asset, blank=True)
    asset = models.ForeignKey(Asset, null=True, blank=True, on_delete=models.CASCADE, related_name='asset')
    watchers = models.ManyToManyField(User, blank=True)
    status_comment = models.CharField(max_length=300, null=True, blank=True)
    being_moved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='mover')
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='approver')
    is_approved = models.BooleanField(default=False)
    date_initiated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_approved = models.DateTimeField(null=True, blank=True)
    date_of_asset_arrival = models.DateTimeField(null=True, blank=True)
    src_department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.CASCADE,
                                       related_name="transferring_department")
    external_company = models.ForeignKey('ExternalCompany', on_delete=models.CASCADE, null=True, blank=True)
    dest_department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.CASCADE,
                                        related_name='receiving_department')
    src_branch = models.ForeignKey(WorkBranch, on_delete=models.CASCADE, null=True, related_name='src_branch')
    dest_branch = models.ForeignKey(WorkBranch, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='dest_branch')
    acknowledged_by_receiver = models.BooleanField(default=False)
    former_custodian = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE,
                                         related_name='former_custodian')
    new_custodian = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE,
                                      related_name='new_custodian')
    received = models.BooleanField(default=False)
    logged_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="user")
    reason = models.ForeignKey(ReasonForTransfer, on_delete=models.CASCADE, related_name="reason", null=True,
                               blank=True)
    draw_back = models.BooleanField(default=False)
    company = models.ForeignKey('ExternalCompany', on_delete=models.CASCADE, null=True, blank=True,
                                related_name="company")
    returned = models.BooleanField(default=False)
    narration = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.reference}'

    class Meta:
        verbose_name = 'Asset Transfer'
        verbose_name_plural = 'Asset Transfers'
        ordering = ['reference']

        permissions = (
            ("can_transfer_internal", "Transfer Internally"),
            ("can_transfer_external", "Transfer Externally"),
            ("can_transfer_asset", "Transfer Asset"),
            ("can_approve_asset_transfer", "Approve Transfer"),
            ("can_assign_asset", "Assign Asset"),
        )


class RoleGroup(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    head = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.group.name


class Specification(models.Model):
    ram_size = models.IntegerField(null=True, )
    processor = models.CharField(max_length=255, null=True, blank=True)
    hdd_size = models.IntegerField()
    has_ssd = models.BooleanField(default=False)
    has_hdd = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.processor} storage: {self.hdd_size} GB ram: {self.ram_size} GB'


class Notification(models.Model):
    id = models.BigAutoField(primary_key=True)
    notification_type = models.CharField(max_length=50, null=False)
    subject = models.CharField(max_length=120)
    content = models.CharField(max_length=1000)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    transfer = models.ForeignKey(AssetTransfer, null=True, blank=True, on_delete=models.CASCADE)
    related_params = models.CharField(max_length=100, null=True)
    date_generated = models.DateTimeField(default=djtimezone.now, null=False)

    class Meta:
        managed = True
        db_table = 'notification'


class ExternalCompany(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True)
    assets_sent = models.ManyToManyField(Asset, blank=True, )
    email = models.EmailField(max_length=255, blank=True, null=True)
    details = models.CharField(max_length=255, null=True)
    tel = models.CharField(max_length=255, null=True)
    cell = models.CharField(max_length=255, null=True)
    contact_person = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ('can_create_company', 'can create company'),
            ('can_delete_company', 'can delete company'),
            ('can_update_company', 'can update company')
        )


class Application(models.Model):
    name = models.CharField(max_length=255, unique=True)
    successifully_installed = models.BooleanField(default=True)
    challenges_faced = models.TextField()

    def __str__(self):
        return self.name


class Configuration(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, related_name='asset_in_configuration',
                              blank=True)
    configured_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='configured_by')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp.date()} {self.configured_by} {self.asset}"


class AssetAssignment(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, related_name='asset_in_assignment',
                              blank=True)
    assigner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='assigner')
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='assignee')
    req = models.ForeignKey('HardwareRequisition', on_delete=models.CASCADE, null=True, blank=True, )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.asset} assigned to {self.assignee}"


class HardwareRequisition(models.Model):
    REASON_FOR_REQUEST = (
        ('VI', 'VIP'),
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low')
    )
    requisitioner = models.ForeignKey(User, related_name='my_hardware_requests', null=True, blank=True,
                                      on_delete=models.SET_NULL)
    designation = models.CharField(max_length=255, null=True, blank=True)
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL)
    date_logged = models.DateField(auto_now_add=True, null=True, blank=True)
    device_requested = models.ForeignKey(AssetCategory, null=False, blank=True, on_delete=models.CASCADE, default=1)
    reason_for_request = models.TextField(blank=True, null=True)
    replacement = models.BooleanField(default=False)
    justification_for_purchase = models.TextField(blank=True, null=True)
    line_manager = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    line_manager_approved = models.BooleanField(default=False)
    line_manager_rejected = models.BooleanField(default=False)
    line_manager_comment = models.TextField(null=True, blank=True)
    authorized_by = models.ForeignKey(User, blank=True, null=True, related_name='authorized_hardware_requests',
                                      on_delete=models.RESTRICT, )
    authorizer_accepted = models.BooleanField(default=False, null=True, blank=True)
    authorizer_rejected = models.BooleanField(default=False, null=True)
    department_decided = models.BooleanField(default=False)
    authorizer_justification = models.TextField(null=True, blank=True)
    infrastructure_manager = models.ForeignKey(User, related_name='infrastructure_manager', on_delete=models.RESTRICT,
                                               null=True, blank=True)
    infrastructure_manager_accepted = models.BooleanField(default=False, null=True)
    infrastructure_manager_rejected = models.BooleanField(default=False, null=True)
    infrastructure_manager_reason_for_action = models.CharField(max_length=255, null=True, blank=True)
    infrastructure_decided = models.BooleanField(default=False)

    head_of_technology_services = models.ForeignKey(User, related_name='head_of_technology_services', blank=True,
                                                    null=True, on_delete=models.RESTRICT)
    head_of_technology_services_accepted = models.BooleanField(default=False, null=True)
    head_of_technology_services_rejected = models.BooleanField(default=False, null=True)
    head_of_technology_services_reason_for_action = models.CharField(max_length=255, null=True, blank=True)
    head_of_technology_services_decided = models.BooleanField(default=False)

    purcharsed = models.BooleanField(default=False)
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.device_requested.name} for {self.requisitioner.username}'

    class Meta:
        ordering = ['device_requested', 'requisitioner']


class UserRights(models.Model):
    requesting_user = models.ForeignKey(User, related_name='requesting_user', null=True, blank=True,
                                        on_delete=models.SET_NULL)
    assignee = models.ForeignKey(User, related_name='rights_assignee', null=True, blank=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(User, related_name='rights_approved_by', null=True, blank=True,
                                    on_delete=models.SET_NULL)
    approved_at = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    watchers = models.ManyToManyField(User, related_name='user_rights_watchers')

#
# class TaskSchedulers(ClockedSchedule):
#
