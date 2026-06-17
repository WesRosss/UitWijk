"""
URL configuration for Tennis Team Website backend.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # API documentation (Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # JWT Authentication endpoints
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # User management endpoints
    path('api/users/', include('tennis_backend.apps.users.urls')),
    
    # Team management endpoints
    path('api/teams/', include('tennis_backend.apps.teams.urls')),
    
    # Match management endpoints
    path('api/matches/', include('tennis_backend.apps.matches.urls')),
    
    # Notification endpoints
    path('api/notifications/', include('tennis_backend.apps.notifications.urls')),
    
    # Health check endpoint
    path('api/health/', include('tennis_backend.apps.api.urls')),
]

# Add static and media URLs for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add WebSocket URL routing
websocket_urlpatterns = []

# For production, you might want to add additional patterns
# For example, to serve the frontend in production:
# urlpatterns += [
#     re_path(r'^.*', TemplateView.as_view(template_name='index.html')),
# ]