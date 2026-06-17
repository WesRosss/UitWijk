"""
Matches app configuration for Tennis Team Website.
"""
from django.apps import AppConfig


class MatchesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tennis_backend.apps.matches'
    verbose_name = 'Match Management'

    def ready(self):
        # Import signals
        import tennis_backend.apps.matches.signals