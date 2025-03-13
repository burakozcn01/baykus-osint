from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Connector(models.Model):
    """
    Connector model represents external services and APIs that the system can connect to.
    """
    CONNECTOR_TYPES = (
        ('social_media', 'Social Media'),
        ('search_engine', 'Search Engine'),
        ('domain_info', 'Domain Information'),
        ('email_verify', 'Email Verification'),
        ('pastebin', 'Pastebin'),
        ('threat_intel', 'Threat Intelligence'),
        ('osint_service', 'OSINT Service'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
        ('rate_limited', 'Rate Limited'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    connector_type = models.CharField(max_length=20, choices=CONNECTOR_TYPES)
    description = models.TextField(blank=True)
    base_url = models.URLField(blank=True)
    documentation_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Configuration
    requires_api_key = models.BooleanField(default=False)
    requires_authentication = models.BooleanField(default=False)
    configuration = models.JSONField(default=dict)  # For storing additional configuration
    
    # Rate limiting
    rate_limit = models.PositiveIntegerField(default=0)  # 0 means no limit
    rate_limit_period = models.CharField(max_length=50, default='')  # e.g., '1m', '1h', '1d'
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_connectors')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_connector_type_display()})"


class APIKey(models.Model):
    """
    APIKey model stores API keys for connectors that require them.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE, related_name='api_keys')
    key_name = models.CharField(max_length=100)
    key_value = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_api_keys')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['connector', 'key_name']
    
    def __str__(self):
        return f"{self.key_name} for {self.connector.name}"


class ConnectorAuth(models.Model):
    """
    ConnectorAuth model stores authentication details for connectors that require it.
    """
    AUTH_TYPES = (
        ('basic', 'Basic Auth'),
        ('oauth1', 'OAuth 1.0'),
        ('oauth2', 'OAuth 2.0'),
        ('token', 'Token Auth'),
        ('cookie', 'Cookie Auth'),
        ('other', 'Other'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE, related_name='auth_credentials')
    auth_type = models.CharField(max_length=20, choices=AUTH_TYPES)
    credentials = models.JSONField()  # Store credentials securely
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_connector_auths')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['connector', 'auth_type']
    
    def __str__(self):
        return f"{self.get_auth_type_display()} for {self.connector.name}"


class ConnectorRequest(models.Model):
    """
    ConnectorRequest model tracks requests made to connectors.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('throttled', 'Throttled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE, related_name='requests')
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)  # GET, POST, etc.
    params = models.JSONField(default=dict)
    headers = models.JSONField(default=dict)
    body = models.TextField(blank=True)
    
    # Response
    status_code = models.IntegerField(null=True, blank=True)
    response_data = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timing
    request_time = models.DateTimeField(auto_now_add=True)
    response_time = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)  # Duration in milliseconds
    
    # Metadata
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='connector_requests')
    
    class Meta:
        ordering = ['-request_time']
    
    def __str__(self):
        return f"{self.method} {self.endpoint} to {self.connector.name}"