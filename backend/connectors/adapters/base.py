"""
Base adapter class that all specific adapters should inherit from.
"""

import requests
import json
import logging
from abc import ABC, abstractmethod
from ..models import APIKey, ConnectorAuth

logger = logging.getLogger(__name__)


class BaseAdapter(ABC):
    """
    Base adapter class for all connector types.
    
    This class defines the interface that all adapters must implement,
    and provides some common functionality.
    """
    
    def __init__(self, connector):
        """
        Initialize the adapter with a connector.
        
        Args:
            connector: The Connector model instance
        """
        self.connector = connector
        self.api_keys = self._get_api_keys()
        self.auth = self._get_auth()
        self.base_url = connector.base_url
        self.configuration = connector.configuration
    
    def _get_api_keys(self):
        """
        Get all active API keys for this connector.
        
        Returns:
            A dictionary mapping key_name to key_value
        """
        if not self.connector.requires_api_key:
            return {}
        
        api_keys = {}
        for key in APIKey.objects.filter(connector=self.connector, is_active=True):
            api_keys[key.key_name] = key.key_value
        
        return api_keys
    
    def _get_auth(self):
        """
        Get all active authentication credentials for this connector.
        
        Returns:
            A dictionary mapping auth_type to credentials
        """
        if not self.connector.requires_authentication:
            return {}
        
        auth = {}
        for cred in ConnectorAuth.objects.filter(connector=self.connector, is_active=True):
            auth[cred.auth_type] = cred.credentials
        
        return auth
    
    def _get_headers(self):
        """
        Get headers for API requests, including any API keys.
        
        Returns:
            A dictionary of headers
        """
        headers = {
            'User-Agent': 'Baykus OSINT Tool/1.0',
            'Accept': 'application/json',
        }
        
        # Add API key to headers if available and required
        if self.api_keys and self.connector.requires_api_key:
            # This is just a basic implementation - actual header format will vary by API
            if 'api_key' in self.api_keys:
                headers['X-API-Key'] = self.api_keys['api_key']
            if 'api_token' in self.api_keys:
                headers['Authorization'] = f"Bearer {self.api_keys['api_token']}"
        
        return headers
    
    def _make_request(self, method, endpoint, params=None, data=None, headers=None):
        """
        Make an HTTP request to the connector API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            headers: Additional headers
            
        Returns:
            tuple: (success, status_code, response_data, error_message)
        """
        url = self._build_url(endpoint)
        request_headers = self._get_headers()
        
        # Add any additional headers
        if headers:
            request_headers.update(headers)
        
        try:
            # Check for rate limiting before making the request
            if self.connector.status == 'rate_limited':
                return False, None, None, "Connector is currently rate limited"
            
            # Make the request
            response = requests.request(
                method,
                url,
                params=params,
                json=data if data else None,
                headers=request_headers,
                timeout=30  # 30 second timeout
            )
            
            # Handle the response
            if response.status_code == 429:  # Too Many Requests
                self.connector.status = 'rate_limited'
                self.connector.save(update_fields=['status'])
                return False, response.status_code, None, "Rate limit exceeded"
            
            try:
                response_data = response.json() if response.content else {}
            except json.JSONDecodeError:
                response_data = response.text
            
            if 200 <= response.status_code < 300:
                return True, response.status_code, response_data, ""
            else:
                return False, response.status_code, response_data, f"API error: {response.status_code}"
                
        except requests.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}")
            return False, None, None, f"Request error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {str(e)}")
            return False, None, None, f"Unexpected error: {str(e)}"
    
    def _build_url(self, endpoint):
        """
        Build the full URL for an API endpoint.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            str: Full URL
        """
        base_url = self.base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')
        return f"{base_url}/{endpoint}"
    
    def test_connection(self):
        """
        Test the connection to the API.
        
        Returns:
            tuple: (success, message)
        """
        # Default implementation that should be overridden by subclasses
        endpoint = self.configuration.get('test_endpoint', '')
        if not endpoint:
            return False, "No test endpoint configured"
        
        success, status_code, _, error_message = self._make_request('GET', endpoint)
        
        if success:
            return True, f"Connection successful with status {status_code}"
        else:
            return False, f"Connection failed: {error_message}"
    
    def execute_request(self, endpoint, method, params=None, headers=None, body=None):
        """
        Execute a request to the API.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters
            headers: Additional headers
            body: Request body
            
        Returns:
            tuple: (success, status_code, response_data, error_message)
        """
        # Parse the body if it's a string
        if body and isinstance(body, str):
            try:
                body_data = json.loads(body)
            except json.JSONDecodeError:
                body_data = {"data": body}
        else:
            body_data = body
        
        return self._make_request(method, endpoint, params, body_data, headers)
    
    @abstractmethod
    def search(self, query, **kwargs):
        """
        Perform a search using the connector.
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            tuple: (success, results, error_message)
        """
        pass
    
    @abstractmethod
    def process_data(self, data):
        """
        Process data received from the connector.
        
        Args:
            data: Data to process
            
        Returns:
            tuple: (success, processed_data, error_message)
        """
        pass