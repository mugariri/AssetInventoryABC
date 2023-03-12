import celery
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from app.celery import start_celery_app
from app.tools import schedule_run
from chatbot.botviews import start_bot

urlpatterns = [
    path('', RedirectView.as_view(url='abcassetsmanager/my_assets'), name='home'),
    path('admin/', admin.site.urls),
    path(r'abcassetsmanager/', include('app.urls', namespace='abcassetsmanager'), name='abcassetsmanager'),
    path('api/', include('app.api_urls', namespace='api'), name='api'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('chatbot/', include('chatbot.urls', namespace='chatbot'), name='chatbot'),
    path('application/', include('application.urls', namespace='application'), name='application'),
]

# start_bot()
# schedule_run()
# c =celery.Celery()
# c.autodiscover_tasks()
# start_celery_app()
