"""
API URLs for Tennis Team Website.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Health check endpoint
    path('health/', views.health_check, name='health_check'),
    
    # API info endpoint
    path('info/', views.api_info, name='api_info'),
    
    # Version endpoint
    path('version/', views.api_version, name='api_version'),
]