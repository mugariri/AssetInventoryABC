from django.contrib import admin

from app.models import Asset, AssetCategory, Department, SubDepartment, Employee, WorkBranch, RoleGroup, \
    Specification, AssetTransfer, TransferType, AssetPool, ReasonForTransfer, ExternalCompany, Application, \
    Configuration, AssetAssignment, HardwareRequisition, AssetClass, General_Ledger


# from import_export.admin import ExportActionMixin

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__last_name', 'user__first_name', 'user__last_name']
    list_display = ['user', 'branch', 'department', 'mobile_number']


admin.site.register(AssetClass)
admin.site.register(AssetCategory)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    search_fields = ['tag', 'serial_tag', 'username']
    empty_value_display = '????'


@admin.register(HardwareRequisition)
class HardwareRequisitionAdmin(admin.ModelAdmin):
    search_fields = ['requisitioner', 'department', ]
    list_display = ['requisitioner', 'department', 'device_requested', 'date_logged']
    # list_editable = ['custodian_user','assigned_to']


# admin.site.register(Configuration)
admin.site.register(AssetAssignment)
admin.site.register(Department)
admin.site.register(SubDepartment)
admin.site.register(WorkBranch)
admin.site.register(AssetTransfer)
admin.site.register(AssetPool)
admin.site.register(TransferType)
admin.site.register(ReasonForTransfer)
admin.site.register(ExternalCompany)
admin.site.register(General_Ledger)
