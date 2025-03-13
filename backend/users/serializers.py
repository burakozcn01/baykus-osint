from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserActivity

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 
                  'is_active', 'is_staff', 'date_joined', 'last_login')
        read_only_fields = ('id', 'date_joined', 'last_login')
    
    def create(self, validated_data):
        """Create and return a new user."""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user
    
    def update(self, instance, validated_data):
        """Update and return an existing user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for the UserActivity model."""
    
    user_email = serializers.SerializerMethodField()
    
    class Meta:
        model = UserActivity
        fields = ('id', 'user', 'user_email', 'activity_type', 'description', 
                  'ip_address', 'user_agent', 'timestamp')
        read_only_fields = ('id', 'timestamp')
    
    def get_user_email(self, obj):
        """Get the email of the user."""
        return obj.user.email if obj.user else None


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password_confirm')
    
    def validate(self, attrs):
        """Validate that the passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs
    
    def create(self, validated_data):
        """Create and return a new user with encrypted password."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user