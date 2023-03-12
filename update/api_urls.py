from django.urls import path

from app.api_views import asset_category_list, asset_category_detail, asset_list, asset_detail, department_list, \
    department_detail, sub_department_list, asset_transfer_list, external_company_list, external_company_details, \
    asset_api_for_app, applications, email_alert

app_name = 'api'

urlpatterns = [
    path('category', asset_category_list, name='asset_category_list'),
    path('category_detail/<int:pk>/', asset_category_detail, name='asset_category_detail'),
    path('asset_list', asset_list, name='asset_list'),
    path('asset_detail/<str:serial_tag>/', asset_detail, name='asset_detail'),
    path('asset_detail/<int:id>/', asset_detail, name='asset_detail'),
    path('department', department_list, name='department_list'),
    path('department_detail/<int:pk>/', department_detail, name='department_detail'),
    path('sub_department', sub_department_list, name='sub_department_list'),
    path('sub_department_detail', department_detail, name='department_detail'),
    path('asset_transfer_list', asset_transfer_list, name='asset_transfer_list'),
    path('external_company_details/<int:pk>/', external_company_details, name='external_company_details'),
    path('external_company_list', external_company_list, name='external_company_list'),
    path('asset_api_for_app/',asset_api_for_app, name='asset_api_for_app'),
    path('applications/', applications, name='applications'),
    path('email_alert/', email_alert, name='email_alert'),
]
