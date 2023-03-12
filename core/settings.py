import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-^iiv*rkz$lwgw9dq)4n%34$z!e3-vq_e4gxo3@$(bg8!39#en4'
DEBUG = True
ALLOWED_HOSTS = ['*']

AUTHENTICATION_BACKENDS = ['bancapis.abc.auth.LDAPAuth']

INSTALLED_APPS = [
    # 'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_celery_beat',
    'app',
    'bancapis',
    'utilitycommands',
    'chatbot',
    'application',
]
MIDDLEWARE = [
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    'app.middleware.SessionExpiredMiddleware',
    'app.middleware.CheckUpdatedEmployee',
    # 'app.middleware.ExceptionHandlingMiddleware',
]
# CACHE_MIDDLEWARE_ALIAS = 'default'
# CACHE_MIDDLEWARE_SECONDS = 600
# CACHE_MIDDLEWARE_PREFIX = ''
ROOT_URLCONF = 'core.urls'

CHANNEL_LAYERS = {
    "default": {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [("localhost", 6379)],
        },
    },
}
# CELERY STUFF
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Harare'
CELERY_TASK_TRACK_STARTED = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context.on_repairs',
                'app.context.gls',
                'app.context.greetings',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = "core.asgi.application"
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'assetmanagementsystem',
#         'USER': 'root',
#         'PASSWORD': '1234',
#         'HOST': 'localhost',
#         'PORT': '2022',
#     }
# }

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
 #       'NAME': BASE_DIR / 'db.sqlite3',
  #  },
#}
# 'default': {
#     'NAME': 'abcassetsmanager',
#      'ENGINE': 'django.db.backends.mysql',
#       'USER': 'root',
#        'PASSWORD': '1234',
#     'HOST': 'localhost',
#      "OPTIONS": {"init_command": "SET default_storage_engine=INNODB;"}
#   },
# }
# DATABASES = {
#   'default': {
#      'ENGINE': 'django.db.backends.mysql',
#      'NAME': 'abcassetsmanager',
#     'USER': 'root',
#     'PASSWORD': '1234',
#    'HOST': 'localhost',
#   'PORT': '3306',
#  }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# EMAIL SETTINGS
# disable this backend to start sending actual emails
# DEFAULT_FROM_EMAIL = 'darlingtonmugariri@gmail.com'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'darlingtonmugariri@gmail.com'
# EMAIL_HOST_PASSWORD = '1857712870'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True

# enable this backend to flow emails
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'outlook.office365.com'
EMAIL_PORT = 587  # 993
EMAIL_HOST_USER = 'abcassetmanager@outlook.com'
EMAIL_HOST_PASSWORD = 'P@ssw0rd@85'

ABC_AUTH_API_USERNAME = 'bancabc'
ABC_AUTH_API_PASSWORD = 'password'
ABC_API_HOST = 'http://10.106.60.5:25183/'
ABC_API_GET_TOKEN = 'api/GetToken'
ABC_API_EMAIL_SEND_SINGLE = 'api/SendEmailDirect'
ABC_API_SMS_SEND_SINGLE = 'api/SmsSendSingle'

PROTOCOL = 'http'
HOST = '10.106.60.5'
#HOST = '127.0.0.1'
PORT = '8000'

USE_L10N = False

DATE_INPUT_FORMATS = ['%d/%m/%Y']

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# SECURITY_SESSION_EXPIRE_AFTER = 30
# SESSION_COOKIE_AGE = 10

LOGIN_PAGE_URL = f'{HOST}:{PORT}/abcassetsmanager/login'

"""
ACTIVE DIRECTORY INTEGRATION
"""
ABC_AUTH_CONFIGURATIONS = [
    {
        'DOMAINS': ["bancabc.co.zw", 'abc.zw'],
        'ABC_AUTH_USER_MANAGEMENT_BACKEND': "WINDOWS_LDAP_BACKEND",
        'ABC_AUTH_LOWER_CASE_USERNAME': 'True',
        'ABC_AUTH_BYPASS_AUTHENTICATION': False,
        'ABC_AUTH_AUTO_CREATE_USER_FROM_AD': True,
        'ABC_AUTH_AUTO_CREATE_USER_CALLBACK': 'app.tools.create_user_from_attributes',
        'ABC_AUTH_AUTHENTICATE_VIA_EXTERNAL_API': False,
        'ABC_AUTH_DESCRIBE_FAILED_AUTHENTICATION': True,
        'ABC_AUTH_DOMAIN_USER_PREFIX': 'abczw',
        'ABC_AUTH_DOMAIN_QUALIFIED_NAME': 'abc.zw',
        'ABC_AUTH_ACTIVE_DIRECTORY_ADDRESS': "ldap://10.106.120.57:389",
        'ABC_AUTH_ADMIN_USER': 'adm-alhomani@abc.zw',
        'ABC_AUTH_ADMIN_PASSWORD': 'P@ssw0rd@85',
        'ABC_AUTH_DOMAIN_UNLOCKED_LOCKOUT_TIME': '1601-01-01 00:00:00+00:00',
        'ABC_AUTH_DOMAIN_DC_CONSTANT': 'dc=abc,dc=zw',
    }
]

"""
    TELEGRAM CHATBOT INTEGRATION
"""

TELEBOT_PARAMOUNT_HANDLERS = [
    "chatbot.my_bot.message_received"
]

"""
    CELERY CONFIGURATIONS
"""

broker_url = 'redis://guest:guest@localhost:5672//'
# BROKER_URL = 'amqp://guest:guest@localhost:5672/'

# List of modules to import when the Celery worker starts.
imports = ('myapp.tasks',)

## Using the database to store task state and results.
result_backend = 'db+sqlite:///results.db'

task_annotations = {'tasks.add': {'rate_limit': '10/s'}}
