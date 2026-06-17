# Settings package
# Import appropriate settings based on environment
from .base import *

# Determine which settings to use
import os

if os.environ.get('DJANGO_SETTINGS_MODULE') == 'tennis_backend.settings.production':
    from .production import *
elif os.environ.get('DJANGO_SETTINGS_MODULE') == 'tennis_backend.settings.development':
    from .development import *
else:
    from .development import *