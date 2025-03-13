"""
Adapter class for Pastebin and similar services.
"""

import logging
from .base import BaseAdapter

logger = logging.getLogger(__name__)


class PastebinAdapter(BaseAdapter):
    """Adapter for Pastebin and similar paste-sharing services."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.service = 'pastebin'
    
    def test_connection(self):
        """Test the connection to the Pastebin service."""
        # Search for a common term to test the connection
        test_query = 'password'
        success, _, _, error_message = self.search_pastes(test_query, limit=1)
        
        if success:
            return True, f"Pastebin service connection successful"
        else:
            return False, f"Pastebin service connection failed: {error_message}"
    
    def search_pastes(self, query, limit=100):
        """
        Search for pastes containing a query.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            tuple: (success, search_results, error_message)
        """
        endpoint = self.configuration.get('search_endpoint', 'search')
        params = {
            'q': query,
            'limit': min(limit, 1000)  # Limit to 1000 or fewer results
        }
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint, params=params)
        
        if success:
            return True, self.process_search_results(response_data), ""
        else:
            return False, None, error_message
    
    def get_paste(self, paste_id):
        """
        Get a specific paste by ID.
        
        Args:
            paste_id: ID of the paste to retrieve
            
        Returns:
            tuple: (success, paste_data, error_message)
        """
        endpoint = self.configuration.get('paste_endpoint', 'paste/{paste_id}')
        endpoint = endpoint.format(paste_id=paste_id)
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint)
        
        if success:
            return True, self.process_paste_data(response_data), ""
        else:
            return False, None, error_message
    
    def process_search_results(self, data):
        """
        Process paste search results.
        
        Args:
            data: Search results to process
            
        Returns:
            dict: Processed search results
        """
        try:
            # Extract the search results
            pastes = data.get('pastes', [])
            
            processed = {
                'service': self.service,
                'type': 'paste_search',
                'query': data.get('query', ''),
                'total_results': len(pastes),
                'results': []
            }
            
            for paste in pastes:
                result = {
                    'id': paste.get('id', ''),
                    'title': paste.get('title', ''),
                    'user': paste.get('user', ''),
                    'date': paste.get('date', ''),
                    'syntax': paste.get('syntax', ''),
                    'size': paste.get('size', 0),
                    'expire': paste.get('expire', ''),
                    'url': paste.get('url', ''),
                    'hits': paste.get('hits', 0),
                    'highlight': paste.get('highlight', '')
                }
                processed['results'].append(result)
            
            return processed
        except Exception as e:
            logger.error(f"Error processing paste search results: {str(e)}")
            return {'service': self.service, 'error': str(e), 'raw_data': data}
    
    def process_paste_data(self, data):
        """
        Process paste data.
        
        Args:
            data: Paste data to process
            
        Returns:
            dict: Processed paste data
        """
        try:
            processed = {
                'service': self.service,
                'type': 'paste',
                'id': data.get('id', ''),
                'title': data.get('title', ''),
                'user': data.get('user', ''),
                'date': data.get('date', ''),
                'syntax': data.get('syntax', ''),
                'size': data.get('size', 0),
                'expire': data.get('expire', ''),
                'url': data.get('url', ''),
                'hits': data.get('hits', 0),
                'content': data.get('content', ''),
                'raw_data': data
            }
            
            return processed
        except Exception as e:
            logger.error(f"Error processing paste data: {str(e)}")
            return {'service': self.service, 'error': str(e), 'raw_data': data}
    
    def search(self, query, **kwargs):
        """
        Perform a search using the connector.
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            tuple: (success, results, error_message)
        """
        search_type = kwargs.get('search_type', 'search')
        
        if search_type == 'search':
            limit = kwargs.get('limit', 100)
            return self.search_pastes(query, limit)
        elif search_type == 'paste':
            return self.get_paste(query)
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
            # Check if this is paste data or search results
            if isinstance(data, dict) and 'content' in data:
                return True, self.process_paste_data(data), ""
            else:
                return True, self.process_search_results(data), ""
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return False, None, f"Error processing data: {str(e)}"