"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()


"""
YOU ONLY NEED ONE OF THESE.
Choose middleware to serve static files. 
WhiteNoise seems to be the go-to but I've used dj-static 
successfully in many production applications.
"""

# If using WhiteNoise:
from whitenoise import WhiteNoise
application = WhiteNoise(get_wsgi_application())

# If using dj-static:
from dj_static import Cling
application = Cling(get_wsgi_application())