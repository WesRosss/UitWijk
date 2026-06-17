"""
API views for Tennis Team Website.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from django.db import connection
import platform
import sys


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """
    Health check endpoint to verify the API is running.
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    health_data = {
        'status': 'healthy' if db_status == "healthy" else 'degraded',
        'database': db_status,
        'timestamp': request.timestamp if hasattr(request, 'timestamp') else None,
    }
    
    return Response(health_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_info(request):
    """
    API information endpoint.
    """
    api_info = {
        'name': 'Tennis Team Website API',
        'version': '1.0.0',
        'description': 'API for managing tennis team competitions, matches, and players',
        'documentation': '/api/docs/',
        'endpoints': {
            'authentication': {
                'token': '/api/auth/token/',
                'refresh': '/api/auth/token/refresh/',
                'verify': '/api/auth/token/verify/',
            },
            'users': '/api/users/',
            'teams': '/api/teams/',
            'matches': '/api/matches/',
            'notifications': '/api/notifications/',
            'health': '/api/health/',
        },
        'environment': settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else 'development',
    }
    
    return Response(api_info, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_version(request):
    """
    API version endpoint.
    """
    version_info = {
        'version': '1.0.0',
        'django_version': settings.DJANGO_VERSION if hasattr(settings, 'DJANGO_VERSION') else 'unknown',
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'server': request.META.get('SERVER_SOFTWARE', 'unknown'),
    }
    
    return Response(version_info, status=status.HTTP_200_OK)