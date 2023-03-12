from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from app.detail_views import asset_list, asset_transfer, transfer_multiple_assets, await_approval, transfer_list, \
    dashboard, acknowledge, user_maintenance_page, create_category, asset_details, transfer_details, my_assets, \
    unacknowledged, create_department, transfer_my_asset, external_transfers, return_asset, assets_on_repairs, \
    assign_asset, give_permissions, hardware_request, approve_hardware_request, pending_requests, all_hardware_requests, \
    infrastructure_manager_pendings, infrastructure_manager_approve, head_of_tech_services_pendings, \
    head_of_tech_services_approve, successiful_request, hardware_request_details, pending_line_manager, \
    line_manager_approve, approve_transfer, printable, printing, print_hardware_request_document
from app.on_views import workstation_deployment
from app.password import password_reset_request
from app.reports import assets_report_for_branch, generate_report, hardware_request_report_for_branch, generate_report_for_department, assets_report_for_department
from app.views import index, user_login, SignUpView, validate_username, register_user, user_logout, employee_update, \
    assets_manager, employee_update, user_update, detailed_data_report

app_name = 'abcassetsmanager'

urlpatterns = [
    # path('', RedirectView.as_view(url='http:/abcassetsmanager/my_assets/'), name='redirect-view'),
    path('login', user_login, name='login'),
    path('printable', printable, name='printable'),
    path('printing', printing, name='print'),
    path('branchassetsreport/<int:branch_id>/', assets_report_for_branch, name='assets_report_for_branch'),
    path('deptassetsreport/<int:dept_id>/', assets_report_for_department, name='assets_report_for_department'),
    path('branchhardwarerequestreport/<int:branch_id>/', hardware_request_report_for_branch, name='hardware_request_report_for_branch'),
    path('generatebranchreport/', generate_report, name='generate_report'),
    path('generatedeptreport/', generate_report_for_department, name='generate_report_for_department'),
    path('logout', user_logout, name='logout'),
    path('validate_username', validate_username, name='validate_username'),
    path('emp', employee_update, name='emp_reg'),
    path('assets-manager', assets_manager, name='assets_manager'),
    path('assets-list', asset_list, name='asset_list'),
    path('asset_transfer/<int:id>/', approve_transfer, name='asset_transfer'),
    # path('approvetransfer/<int:id>/', approve_transfer, name='approve_transfer'),
    path('transfer_multiple', transfer_multiple_assets, name='transfer_multiple_assets'),
    path('awaiting_approval', await_approval, name='awaiting_approval'),
    path('transfer_list', transfer_list, name='transfer_list'),
    path('dashboard', dashboard, name='dashboard'),
    path('acknowledge/<int:id>/', acknowledge, name='acknowledge'),
    path('user_maintenance_page', user_maintenance_page, name='user_maintenance_page'),
    path('create_category', create_category, name='create_category'),
    path('asset_details/<int:asset_id>/', asset_details, name='asset_details'),
    path('transfer_details/<int:transfer_id>/', transfer_details, name='transfer_details'),
    path('my_assets', my_assets, name='my_assets'),
    path('permissions', give_permissions, name='give_permissions'),
    path('create_departments', create_department, name='create_departments'),
    path('unacknowledged', unacknowledged, name='unacknowledged'),
    path('transfer-my-asset', transfer_my_asset, name='transfer_my_asset'),
    path('external-transfers', external_transfers, name='external_transfers'),
    path('outforrepairs', assets_on_repairs, name='assets_on_repairs'),
    path('assignasset', assign_asset, name='assign_asset'),
    path('profileupdate/', user_update, name='user_update'),
    path('inmanagerpendings', infrastructure_manager_pendings, name='infrastructure_manager_pendings'),
    path('headoftechservicespendings', head_of_tech_services_pendings, name='head_of_tech_services_pendings'),
    path('inmanagerapprove/<int:id>/', infrastructure_manager_approve, name='infrastructure_manager_approve'),
    path('headoftechservicesapprove/<int:id>/', head_of_tech_services_approve, name='head_of_tech_services_approve'),
    path('hardwarerequest', hardware_request, name='hardware_request'),
    path('return_asset/<int:id>/', return_asset, name='return_asset'),
    path('pendingrequests', pending_requests, name='pending_requests'),
    path('allhardwarerequests', all_hardware_requests, name='all_hardware_requests'),
    path('successifulrequest', successiful_request, name='successiful_request'),
    path('hardwarerequestdetails/<int:id>/', hardware_request_details, name='hardware_request_details'),
    path('approvehardwarerequest/<int:id>/', approve_hardware_request, name='approve_hardware_request'),
    path('workstation_deployment/<int:asset_id>/', workstation_deployment, name='workstation_deployment'),
    path('linemanagerapprove/<int:id>/', line_manager_approve, name='line_manager_approve'),
    path('pendinglinemanager', pending_line_manager, name='pending_line_manager'),
    path('detailed-data-report', detailed_data_report, name='detailed_data_report'),
    path('<int:id>/print-hardware-request-document', print_hardware_request_document, name='print_hardware_request_document'),
]
