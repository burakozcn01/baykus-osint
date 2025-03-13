from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, 
    UserActivitySerializer, 
    UserRegistrationSerializer
)
from .models import UserActivity

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get the current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me_update(self, request):
        """Update the current user profile."""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing user activities.
    """
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['user', 'activity_type']
    
    def get_queryset(self):
        """
        By default, users can only see their own activities,
        unless they are staff users who can see all activities.
        """
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserLoginView(TokenObtainPairView):
    """
    API endpoint for user login.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """
        Record user login activity.
        """
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            user_email = request.data.get('email')
            try:
                user = User.objects.get(email=user_email)
                UserActivity.objects.create(
                    user=user,
                    activity_type='login',
                    description='User logged in',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except User.DoesNotExist:
                pass
        
        return response
    
    def get_client_ip(self, request):
        """Get the client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip