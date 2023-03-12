from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url



from .views import *
urlpatterns = [
    path('accounts/login',login_view),
    path('accounts/savePasswordChange',save_password_change),
    path('accounts/requestPasswordChange',request_password_change),
    path('accounts/applyPasswordChange/<str:username>/<str:token>/<str:signature>',apply_password_change),
]




