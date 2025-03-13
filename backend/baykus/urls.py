from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API Schema documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Baykuş OSINT API",
        default_version='v1',
        description="API for Baykuş OSINT tool",
        terms_of_service="",
        contact=openapi.Contact(email=""),
        license=openapi.License(name=""),
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticated],
)

api_urlpatterns = [
    path('users/', include('users.urls')),
    path('core/', include('core.urls')),
    path('connectors/', include('connectors.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include(api_urlpatterns)),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)