from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, UserActivityViewSet, RegisterView, UserLoginView

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'', UserViewSet)
router.register(r'activities', UserActivityViewSet)

# URL patterns for user authentication and management
urlpatterns = [
    # Router based urls
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('profile/', UserViewSet.as_view({'get': 'me', 'put': 'me_update', 'patch': 'me_update'}), name='profile'),
]