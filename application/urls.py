from django.urls import path

from application.views import deployment, uncleared, clear, deployments, deploy, cleared, user_logout, mine, update, user_login

app_name = 'application'

urlpatterns = [
    path('deploy/', deploy, name='deploy'),
    path('update/<int:id>/', update, name='update'),
    path('mine/', mine, name='mine'),
    path('deployments/', deployments, name='deployments'),
    path('deployment/<int:id>/', deployment, name='deployment'),
    path('uncleared/', uncleared, name='uncleared'),
    path('clear/<int:id>/', clear, name='clear'),
    path('cleared/', cleared, name='cleared'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]
