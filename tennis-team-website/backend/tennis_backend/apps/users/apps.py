"""
Users app configuration for Tennis Team Website.
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tennis_backend.apps.users'
    verbose_name = 'User Management'

    def ready(self):
        # Import signals
        import tennis_backend.apps.users.signals