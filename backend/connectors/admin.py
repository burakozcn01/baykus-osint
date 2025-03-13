from django.contrib import admin
from .models import Connector, APIKey, ConnectorAuth, ConnectorRequest


@admin.register(Connector)
class ConnectorAdmin(admin.ModelAdmin):
    """Admin configuration for the Connector model."""
    
    list_display = ('name', 'connector_type', 'status', 'requires_api_key', 'requires_authentication', 'created_at')
    list_filter = ('connector_type', 'status', 'requires_api_key', 'requires_authentication')
    search_fields = ('name', 'description', 'base_url')
    readonly_fields = ('created_by', 'created_at', 'updated_at')


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Admin configuration for the APIKey model."""
    
    list_display = ('connector', 'key_name', 'is_active', 'created_by', 'created_at')
    list_filter = ('connector', 'is_active', 'created_at')
    search_fields = ('connector__name', 'key_name')
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    
    def get_fields(self, request, obj=None):
        """Hide the actual API key value in the admin except when creating a new key."""
        fields = super().get_fields(request, obj)
        if obj:  # Editing an existing object
            fields = [f for f in fields if f != 'key_value']
        return fields


@admin.register(ConnectorAuth)
class ConnectorAuthAdmin(admin.ModelAdmin):
    """Admin configuration for the ConnectorAuth model."""
    
    list_display = ('connector', 'auth_type', 'is_active', 'created_by', 'created_at')
    list_filter = ('connector', 'auth_type', 'is_active', 'created_at')
    search_fields = ('connector__name',)
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    
    def get_fields(self, request, obj=None):
        """Hide the actual credentials in the admin except when creating a new auth."""
        fields = super().get_fields(request, obj)
        if obj:  # Editing an existing object
            fields = [f for f in fields if f != 'credentials']
        return fields


@admin.register(ConnectorRequest)
class ConnectorRequestAdmin(admin.ModelAdmin):
    """Admin configuration for the ConnectorRequest model."""
    
    list_display = ('connector', 'endpoint', 'method', 'status', 'status_code', 'request_time', 'duration_ms')
    list_filter = ('connector', 'method', 'status', 'request_time')
    search_fields = ('connector__name', 'endpoint', 'error_message')
    readonly_fields = (
        'connector', 'endpoint', 'method', 'params', 'headers', 'body', 
        'status_code', 'response_data', 'error_message', 'status', 
        'request_time', 'response_time', 'duration_ms', 'requested_by'
    )
    
    def has_add_permission(self, request):
        """Disable the ability to add requests manually."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable the ability to modify requests."""
        return False