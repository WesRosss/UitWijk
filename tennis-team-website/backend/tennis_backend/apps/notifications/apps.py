"""
Notifications app configuration for Tennis Team Website.
"""
from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tennis_backend.apps.notifications'
    verbose_name = 'Notification System'

    def ready(self):
        # Import signals
        import tennis_backend.apps.notifications.signals