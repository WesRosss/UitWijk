"""
WSGI config for Tennis Team Website backend.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``startproject``
commands use this application when starting the development server.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tennis_backend.settings')

application = get_wsgi_application()