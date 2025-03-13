"""
Adapter class for username search services.
"""

import logging
import re
from .base import BaseAdapter

logger = logging.getLogger(__name__)


class UsernameSearchAdapter(BaseAdapter):
    """Adapter for username search services that check username availability across platforms."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.service = 'username_search'
    
    def test_connection(self):
        """Test the connection to the username search service."""
        # Use a common username as a test
        test_username = 'test'
        success, _, _, error_message = self.search_username(test_username, limit=1)
        
        if success:
            return True, f"Username search service connection successful"
        else:
            return False, f"Username search service connection failed: {error_message}"
    
    def search_username(self, username, limit=None):
        """
        Search for a username across platforms.
        
        Args:
            username: Username to search for
            limit: Maximum number of platforms to check (None for all)
            
        Returns:
            tuple: (success, search_results, error_message)
        """
        # Validate username format
        if not self._is_valid_username(username):
            return False, None, f"Invalid username format: {username}"
        
        endpoint = self.configuration.get('search_endpoint', 'search')
        params = {'username': username}
        
        if limit:
            params['limit'] = limit
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint, params=params)
        
        if success:
            return True, self.process_search_results(response_data), ""
        else:
            return False, None, error_message
    
    def check_platform(self, username, platform):
        """
        Check a username on a specific platform.
        
        Args:
            username: Username to check
            platform: Platform to check (e.g., 'twitter', 'github')
            
        Returns:
            tuple: (success, platform_data, error_message)
        """
        # Validate username format
        if not self._is_valid_username(username):
            return False, None, f"Invalid username format: {username}"
        
        endpoint = self.configuration.get('platform_endpoint', 'check/{platform}')
        endpoint = endpoint.format(platform=platform)
        params = {'username': username}
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint, params=params)
        
        if success:
            return True, self.process_platform_data(response_data), ""
        else:
            return False, None, error_message
    
    def _is_valid_username(self, username):
        """
        Check if a username has a valid format.
        
        Args:
            username: Username to check
            
        Returns:
            bool: True if the username format is valid, False otherwise
        """
        # Basic username validation (alphanumeric, underscore, period, hyphen)
        pattern = r'^[a-zA-Z0-9._-]+$'
        return bool(re.match(pattern, username)) and len(username) <= 30
    
    def process_search_results(self, data):
        """
        Process username search results.
        
        Args:
            data: Search results to process
            
        Returns:
            dict: Processed search results
        """
        try:
            # Extract the search results
            results = data.get('results', [])
            
            processed = {
                'service': self.service,
                'type': 'username_search',
                'username': data.get('username', ''),
                'total_sites': len(results),
                'found': [],
                'not_found': [],
                'error': []
            }
            
            for result in results:
                platform = result.get('platform', '')
                status = result.get('status', '')
                
                if status == 'found':
                    processed['found'].append({
                        'platform': platform,
                        'url': result.get('url', ''),
                        'username': result.get('username', '')
                    })
                elif status == 'not_found':
                    processed['not_found'].append({
                        'platform': platform
                    })
                elif status == 'error':
                    processed['error'].append({
                        'platform': platform,
                        'error': result.get('error', '')
                    })
            
            # Calculate presence percentage
            if processed['total_sites'] > 0:
                processed['presence_percentage'] = (len(processed['found']) / processed['total_sites']) * 100
            else:
                processed['presence_percentage'] = 0
            
            return processed
        except Exception as e:
            logger.error(f"Error processing username search results: {str(e)}")
            return {'service': self.service, 'error': str(e), 'raw_data': data}
    
    def process_platform_data(self, data):
        """
        Process platform-specific data.
        
        Args:
            data: Platform data to process
            
        Returns:
            dict: Processed platform data
        """
        try:
            processed = {
                'service': self.service,
                'type': 'platform_check',
                'username': data.get('username', ''),
                'platform': data.get('platform', ''),
                'status': data.get('status', ''),
                'url': data.get('url', ''),
                'raw_data': data
            }
            
            return processed
        except Exception as e:
            logger.error(f"Error processing platform data: {str(e)}")
            return {'service': self.service, 'error': str(e), 'raw_data': data}
    
    def search(self, query, **kwargs):
        """
        Perform a search using the connector.
        
        Args:
            query: Username to search for
            **kwargs: Additional search parameters
            
        Returns:
            tuple: (success, results, error_message)
        """
        search_type = kwargs.get('search_type', 'search')
        
        if search_type == 'search':
            limit = kwargs.get('limit', None)
            return self.search_username(query, limit)
        elif search_type == 'platform':
            platform = kwargs.get('platform')
            if not platform:
                return False, None, "Platform parameter is required for platform search type"
            return self.check_platform(query, platform)
        else:
            return False, None, f"Unsupported search type: {search_type}"
    
    def process_data(self, data):
        """
        Process data received from the connector.
        
        Args:
            data: Data to process
            
        Returns:
            tuple: (success, processed_data, error_message)
        """
        try:
            # Check if this is platform data or search results
            if isinstance(data, dict) and 'platform' in data and 'username' in data:
                return True, self.process_platform_data(data), ""
            else:
                return True, self.process_search_results(data), ""
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return False, None, f"Error processing data: {str(e)}"