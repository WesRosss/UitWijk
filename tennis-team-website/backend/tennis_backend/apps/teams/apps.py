"""
Teams app configuration for Tennis Team Website.
"""
from django.apps import AppConfig


class TeamsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tennis_backend.apps.teams'
    verbose_name = 'Team Management'

    def ready(self):
        # Import signals
        import tennis_backend.apps.teams.signals