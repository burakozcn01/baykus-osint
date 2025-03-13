from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TargetViewSet, AssetTypeViewSet, AssetViewSet, ScanResultViewSet,
    DorkViewSet, DorkResultViewSet, RelationshipViewSet, ReportViewSet, AlertViewSet
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'targets', TargetViewSet)
router.register(r'asset-types', AssetTypeViewSet)
router.register(r'assets', AssetViewSet)
router.register(r'scan-results', ScanResultViewSet)
router.register(r'dorks', DorkViewSet)
router.register(r'dork-results', DorkResultViewSet)
router.register(r'relationships', RelationshipViewSet)
router.register(r'reports', ReportViewSet)
router.register(r'alerts', AlertViewSet)

# URL patterns for the core app
urlpatterns = [
    path('', include(router.urls)),
]