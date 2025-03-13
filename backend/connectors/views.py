from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Connector, APIKey, ConnectorAuth, ConnectorRequest
from .serializers import (
    ConnectorSerializer, APIKeySerializer, 
    ConnectorAuthSerializer, ConnectorRequestSerializer
)

# Import adapter classes (to be implemented later)
from .adapters import get_adapter_for_connector


class ConnectorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing connectors.
    """
    queryset = Connector.objects.all()
    serializer_class = ConnectorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['connector_type', 'status', 'requires_api_key', 'requires_authentication', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test the connection to a connector."""
        connector = self.get_object()
        
        # Get the appropriate adapter for this connector
        adapter = get_adapter_for_connector(connector)
        if not adapter:
            return Response({'error': f'No adapter available for connector type: {connector.connector_type}'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Attempt to test the connection
        success, message = adapter.test_connection()
        
        if success:
            connector.status = 'active'
            connector.save()
            return Response({'status': 'success', 'message': message})
        else:
            connector.status = 'error'
            connector.save()
            return Response({'status': 'error', 'message': message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def api_keys(self, request, pk=None):
        """Get API keys for a specific connector."""
        connector = self.get_object()
        api_keys = APIKey.objects.filter(connector=connector)
        serializer = APIKeySerializer(api_keys, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def auth_credentials(self, request, pk=None):
        """Get authentication credentials for a specific connector."""
        connector = self.get_object()
        auth_credentials = ConnectorAuth.objects.filter(connector=connector)
        serializer = ConnectorAuthSerializer(auth_credentials, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def requests(self, request, pk=None):
        """Get request history for a specific connector."""
        connector = self.get_object()
        connector_requests = ConnectorRequest.objects.filter(connector=connector)[:100]  # Limit to 100 most recent
        serializer = ConnectorRequestSerializer(connector_requests, many=True, context={'request': request})
        return Response(serializer.data)


class APIKeyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing API keys.
    """
    queryset = APIKey.objects.all()
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['connector', 'is_active', 'created_by']
    ordering_fields = ['key_name', 'created_at', 'updated_at']


class ConnectorAuthViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing connector authentication.
    """
    queryset = ConnectorAuth.objects.all()
    serializer_class = ConnectorAuthSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['connector', 'auth_type', 'is_active', 'created_by']
    ordering_fields = ['auth_type', 'created_at', 'updated_at']


class ConnectorRequestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing connector requests.
    """
    queryset = ConnectorRequest.objects.all()
    serializer_class = ConnectorRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['connector', 'method', 'status', 'requested_by']
    ordering_fields = ['request_time', 'duration_ms']
    
    @action(detail=False, methods=['post'])
    def execute(self, request):
        """Execute a request to a connector."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract data from the serializer
        connector_id = serializer.validated_data.get('connector').id
        endpoint = serializer.validated_data.get('endpoint')
        method = serializer.validated_data.get('method')
        params = serializer.validated_data.get('params', {})
        headers = serializer.validated_data.get('headers', {})
        body = serializer.validated_data.get('body', '')
        
        try:
            # Get the connector
            connector = Connector.objects.get(pk=connector_id)
            
            # Create a new connector request
            connector_request = ConnectorRequest.objects.create(
                connector=connector,
                endpoint=endpoint,
                method=method,
                params=params,
                headers=headers,
                body=body,
                status='pending',
                requested_by=request.user
            )
            
            # Get the adapter for this connector
            adapter = get_adapter_for_connector(connector)
            if not adapter:
                connector_request.status = 'error'
                connector_request.error_message = f'No adapter available for connector type: {connector.connector_type}'
                connector_request.save()
                return Response(
                    {'error': connector_request.error_message}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Execute the request
            start_time = timezone.now()
            success, status_code, response_data, error_message = adapter.execute_request(
                endpoint, method, params, headers, body
            )
            end_time = timezone.now()
            
            # Update the connector request with the results
            connector_request.status = 'success' if success else 'error'
            connector_request.status_code = status_code
            connector_request.response_data = response_data
            connector_request.error_message = error_message
            connector_request.response_time = end_time
            connector_request.duration_ms = int((end_time - start_time).total_seconds() * 1000)
            connector_request.save()
            
            # Return the updated connector request
            serializer = self.get_serializer(connector_request)
            return Response(serializer.data)
            
        except Connector.DoesNotExist:
            return Response({'error': 'Connector not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)