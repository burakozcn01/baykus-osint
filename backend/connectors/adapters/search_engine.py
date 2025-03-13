"""
Adapter classes for search engine services.
"""

import logging
import urllib.parse
from .base import BaseAdapter

logger = logging.getLogger(__name__)


class SearchEngineAdapter(BaseAdapter):
    """Base class for search engine adapters with common functionality."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.engine = None  # To be set by subclasses
    
    def search_web(self, query, num_results=10, start=0):
        """
        Perform a web search.
        
        Args:
            query: Search query
            num_results: Number of results to return
            start: Start index for pagination
            
        Returns:
            tuple: (success, search_results, error_message)
        """
        endpoint = self.configuration.get('search_endpoint', 'search')
        params = {
            'q': query,
            'num': min(num_results, 100),  # Limit to 100 or fewer results
            'start': start
        }
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint, params=params)
        
        if success:
            return True, self.process_search_results(response_data), ""
        else:
            return False, None, error_message
    
    def search_images(self, query, num_results=10, start=0):
        """
        Perform an image search.
        
        Args:
            query: Search query
            num_results: Number of results to return
            start: Start index for pagination
            
        Returns:
            tuple: (success, image_results, error_message)
        """
        endpoint = self.configuration.get('image_search_endpoint', 'images')
        params = {
            'q': query,
            'num': min(num_results, 100),  # Limit to 100 or fewer results
            'start': start
        }
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint, params=params)
        
        if success:
            return True, self.process_image_results(response_data), ""
        else:
            return False, None, error_message
    
    def search_dork(self, dork_query, num_results=10, start=0):
        """
        Perform a search using a Google dork query.
        
        Args:
            dork_query: Google dork query
            num_results: Number of results to return
            start: Start index for pagination
            
        Returns:
            tuple: (success, dork_results, error_message)
        """
        # For most search engines, a dork query is just a special search query
        return self.search_web(dork_query, num_results, start)
    
    def process_search_results(self, data):
        """
        Process web search results.
        
        Args:
            data: Search results to process
            
        Returns:
            dict: Processed search results
        """
        # Default implementation that should be overridden by subclasses
        return {
            'engine': self.engine,
            'type': 'web_search',
            'raw_data': data
        }
    
    def process_image_results(self, data):
        """
        Process image search results.
        
        Args:
            data: Image search results to process
            
        Returns:
            dict: Processed image results
        """
        # Default implementation that should be overridden by subclasses
        return {
            'engine': self.engine,
            'type': 'image_search',
            'raw_data': data
        }
    
    def search(self, query, **kwargs):
        """
        Perform a search using the connector.
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            tuple: (success, results, error_message)
        """
        search_type = kwargs.get('search_type', 'web')
        num_results = kwargs.get('num_results', 10)
        start = kwargs.get('start', 0)
        
        if search_type == 'web':
            return self.search_web(query, num_results, start)
        elif search_type == 'images':
            return self.search_images(query, num_results, start)
        elif search_type == 'dork':
            return self.search_dork(query, num_results, start)
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
            # This is a basic implementation - actual processing will depend on the data
            processed_data = {
                'engine': self.engine,
                'data_type': 'search_results',
                'raw_data': data
            }
            
            return True, processed_data, ""
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return False, None, f"Error processing data: {str(e)}"


class GoogleAdapter(SearchEngineAdapter):
    """Adapter for the Google Search API."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.engine = 'google'
    
    def test_connection(self):
        """Test the connection to the Google Search API."""
        # Use a simple search as a test
        test_query = 'test'
        success, _, _, error_message = self.search_web(test_query, 1)
        
        if success:
            return True, f"Google Search API connection successful"
        else:
            return False, f"Google Search API connection failed: {error_message}"
    
    def process_search_results(self, data):
        """Process Google web search results."""
        try:
            # Extract the search results
            items = data.get('items', [])
            
            processed = {
                'engine': self.engine,
                'type': 'web_search',
                'query': data.get('queries', {}).get('request', [{}])[0].get('searchTerms', ''),
                'total_results': data.get('searchInformation', {}).get('totalResults', 0),
                'results': []
            }
            
            for item in items:
                result = {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'display_link': item.get('displayLink', ''),
                    'cache_link': item.get('cacheId', None),
                    'mime_type': item.get('mime', ''),
                    'file_format': item.get('fileFormat', '')
                }
                processed['results'].append(result)
            
            return processed
        except Exception as e:
            logger.error(f"Error processing Google search results: {str(e)}")
            return {'engine': self.engine, 'error': str(e), 'raw_data': data}
    
    def process_image_results(self, data):
        """Process Google image search results."""
        try:
            # Extract the image search results
            items = data.get('items', [])
            
            processed = {
                'engine': self.engine,
                'type': 'image_search',
                'query': data.get('queries', {}).get('request', [{}])[0].get('searchTerms', ''),
                'total_results': data.get('searchInformation', {}).get('totalResults', 0),
                'results': []
            }
            
            for item in items:
                result = {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'display_link': item.get('displayLink', ''),
                    'mime_type': item.get('mime', ''),
                    'file_format': item.get('fileFormat', ''),
                    'image': {
                        'context_link': item.get('image', {}).get('contextLink', ''),
                        'height': item.get('image', {}).get('height', 0),
                        'width': item.get('image', {}).get('width', 0),
                        'thumbnail_link': item.get('image', {}).get('thumbnailLink', ''),
                        'thumbnail_height': item.get('image', {}).get('thumbnailHeight', 0),
                        'thumbnail_width': item.get('image', {}).get('thumbnailWidth', 0),
                    }
                }
                processed['results'].append(result)
            
            return processed
        except Exception as e:
            logger.error(f"Error processing Google image results: {str(e)}")
            return {'engine': self.engine, 'error': str(e), 'raw_data': data}


class BingAdapter(SearchEngineAdapter):
    """Adapter for the Bing Search API."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.engine = 'bing'
    
    def test_connection(self):
        """Test the connection to the Bing Search API."""
        # Use a simple search as a test
        test_query = 'test'
        success, _, _, error_message = self.search_web(test_query, 1)
        
        if success:
            return True, f"Bing Search API connection successful"
        else:
            return False, f"Bing Search API connection failed: {error_message}"
    
    def _get_headers(self):
        """Get headers for Bing API requests."""
        headers = super()._get_headers()
        
        # Bing requires the API key to be in the 'Ocp-Apim-Subscription-Key' header
        if self.api_keys and 'subscription_key' in self.api_keys:
            headers['Ocp-Apim-Subscription-Key'] = self.api_keys['subscription_key']
        
        return headers
    
    def process_search_results(self, data):
        """Process Bing web search results."""
        try:
            # Extract the search results
            web_pages = data.get('webPages', {}).get('value', [])
            
            processed = {
                'engine': self.engine,
                'type': 'web_search',
                'query': data.get('queryContext', {}).get('originalQuery', ''),
                'total_results': data.get('webPages', {}).get('totalEstimatedMatches', 0),
                'results': []
            }
            
            for page in web_pages:
                result = {
                    'title': page.get('name', ''),
                    'link': page.get('url', ''),
                    'snippet': page.get('snippet', ''),
                    'display_link': page.get('displayUrl', ''),
                    'date_last_crawled': page.get('dateLastCrawled', '')
                }
                processed['results'].append(result)
            
            return processed
        except Exception as e:
            logger.error(f"Error processing Bing search results: {str(e)}")
            return {'engine': self.engine, 'error': str(e), 'raw_data': data}
    
    def process_image_results(self, data):
        """Process Bing image search results."""
        try:
            # Extract the image search results
            images = data.get('value', [])
            
            processed = {
                'engine': self.engine,
                'type': 'image_search',
                'query': data.get('queryContext', {}).get('originalQuery', ''),
                'total_results': data.get('totalEstimatedMatches', 0),
                'results': []
            }
            
            for image in images:
                result = {
                    'title': image.get('name', ''),
                    'link': image.get('contentUrl', ''),
                    'host_page_url': image.get('hostPageUrl', ''),
                    'host_page_display_url': image.get('hostPageDisplayUrl', ''),
                    'content_size': image.get('contentSize', ''),
                    'width': image.get('width', 0),
                    'height': image.get('height', 0),
                    'thumbnail_url': image.get('thumbnailUrl', ''),
                    'thumbnail_width': image.get('thumbnail', {}).get('width', 0),
                    'thumbnail_height': image.get('thumbnail', {}).get('height', 0),
                    'image_insights_token': image.get('imageInsightsToken', '')
                }
                processed['results'].append(result)
            
            return processed
        except Exception as e:
            logger.error(f"Error processing Bing image results: {str(e)}")
            return {'engine': self.engine, 'error': str(e), 'raw_data': data}