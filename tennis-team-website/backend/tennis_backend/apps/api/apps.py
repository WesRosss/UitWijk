"""
API app configuration for Tennis Team Website.
"""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tennis_backend.apps.api'
    verbose_name = 'API'

    def ready(self):
        # Import signals if needed
        pass