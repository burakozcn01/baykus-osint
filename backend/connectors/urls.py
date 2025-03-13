from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConnectorViewSet, APIKeyViewSet, 
    ConnectorAuthViewSet, ConnectorRequestViewSet
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'connectors', ConnectorViewSet)
router.register(r'api-keys', APIKeyViewSet)
router.register(r'auth-credentials', ConnectorAuthViewSet)
router.register(r'requests', ConnectorRequestViewSet)

# URL patterns for the connectors app
urlpatterns = [
    path('', include(router.urls)),
]