from rest_framework import serializers
from .models import Connector, APIKey, ConnectorAuth, ConnectorRequest


class ConnectorSerializer(serializers.ModelSerializer):
    """Serializer for the Connector model."""
    
    created_by_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Connector
        fields = (
            'id', 'name', 'connector_type', 'description', 'base_url', 
            'documentation_url', 'status', 'requires_api_key', 
            'requires_authentication', 'configuration', 'rate_limit', 
            'rate_limit_period', 'created_by', 'created_by_email', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')
    
    def get_created_by_email(self, obj):
        """Get the email of the user who created the connector."""
        return obj.created_by.email if obj.created_by else None
    
    def create(self, validated_data):
        """Create a new connector and associate it with the current user."""
        user = self.context['request'].user
        connector = Connector.objects.create(created_by=user, **validated_data)
        return connector


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for the APIKey model."""
    
    connector_name = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    key_value = serializers.CharField(write_only=True)
    masked_key_value = serializers.SerializerMethodField()
    
    class Meta:
        model = APIKey
        fields = (
            'id', 'connector', 'connector_name', 'key_name', 'key_value', 
            'masked_key_value', 'is_active', 'created_by', 'created_by_email', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at', 'masked_key_value')
    
    def get_connector_name(self, obj):
        """Get the name of the connector."""
        return obj.connector.name
    
    def get_created_by_email(self, obj):
        """Get the email of the user who created the API key."""
        return obj.created_by.email if obj.created_by else None
    
    def get_masked_key_value(self, obj):
        """Get a masked version of the API key for display purposes."""
        if obj.key_value:
            if len(obj.key_value) <= 8:
                return "*" * len(obj.key_value)
            return obj.key_value[:4] + "*" * (len(obj.key_value) - 8) + obj.key_value[-4:]
        return ""
    
    def create(self, validated_data):
        """Create a new API key and associate it with the current user."""
        user = self.context['request'].user
        api_key = APIKey.objects.create(created_by=user, **validated_data)
        return api_key


class ConnectorAuthSerializer(serializers.ModelSerializer):
    """Serializer for the ConnectorAuth model."""
    
    connector_name = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    credentials = serializers.JSONField(write_only=True)
    
    class Meta:
        model = ConnectorAuth
        fields = (
            'id', 'connector', 'connector_name', 'auth_type', 'credentials', 
            'is_active', 'created_by', 'created_by_email', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')
    
    def get_connector_name(self, obj):
        """Get the name of the connector."""
        return obj.connector.name
    
    def get_created_by_email(self, obj):
        """Get the email of the user who created the connector auth."""
        return obj.created_by.email if obj.created_by else None
    
    def create(self, validated_data):
        """Create a new connector auth and associate it with the current user."""
        user = self.context['request'].user
        connector_auth = ConnectorAuth.objects.create(created_by=user, **validated_data)
        return connector_auth


class ConnectorRequestSerializer(serializers.ModelSerializer):
    """Serializer for the ConnectorRequest model."""
    
    connector_name = serializers.SerializerMethodField()
    requested_by_email = serializers.SerializerMethodField()
    
    class Meta:
        model = ConnectorRequest
        fields = (
            'id', 'connector', 'connector_name', 'endpoint', 'method', 
            'params', 'headers', 'body', 'status_code', 'response_data', 
            'error_message', 'status', 'request_time', 'response_time', 
            'duration_ms', 'requested_by', 'requested_by_email'
        )
        read_only_fields = ('id', 'status_code', 'response_data', 'error_message', 
                           'status', 'request_time', 'response_time', 'duration_ms', 
                           'requested_by')
    
    def get_connector_name(self, obj):
        """Get the name of the connector."""
        return obj.connector.name
    
    def get_requested_by_email(self, obj):
        """Get the email of the user who made the request."""
        return obj.requested_by.email if obj.requested_by else None
    
    def create(self, validated_data):
        """Create a new connector request and associate it with the current user."""
        user = self.context['request'].user
        connector_request = ConnectorRequest.objects.create(requested_by=user, **validated_data)
        return connector_request