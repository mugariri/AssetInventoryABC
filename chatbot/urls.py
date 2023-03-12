from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from chatbot import botviews
# from chatbot.views import assetmanagerchatbotview

app_name = 'chatbot'

urlpatterns = [
    # path('assetmanagerchatbotview/', assetmanagerchatbotview, name='assetmanagerchatbotview'),
]
