"""
Adapter classes for social media platforms.
"""

import logging
from .base import BaseAdapter

logger = logging.getLogger(__name__)


class SocialMediaAdapter(BaseAdapter):
    """Base class for social media adapters with common functionality."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.platform = None  # To be set by subclasses
    
    def get_profile(self, username):
        """
        Get a social media profile by username.
        
        Args:
            username: Username to look up
            
        Returns:
            tuple: (success, profile_data, error_message)
        """
        endpoint = self.configuration.get('profile_endpoint', 'users/{username}')
        endpoint = endpoint.format(username=username)
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint)
        
        if success:
            return True, self.process_profile_data(response_data), ""
        else:
            return False, None, error_message
    
    def search_posts(self, query, max_results=100):
        """
        Search for posts using a query.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            tuple: (success, posts_data, error_message)
        """
        endpoint = self.configuration.get('search_endpoint', 'search')
        params = {
            'q': query,
            'count': min(max_results, 100)  # Limit to 100 or fewer results
        }
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint, params=params)
        
        if success:
            return True, self.process_search_data(response_data), ""
        else:
            return False, None, error_message
    
    def process_profile_data(self, data):
        """
        Process profile data received from the API.
        
        Args:
            data: Profile data to process
            
        Returns:
            dict: Processed profile data
        """
        # Default implementation that should be overridden by subclasses
        return {
            'platform': self.platform,
            'raw_data': data
        }
    
    def process_search_data(self, data):
        """
        Process search data received from the API.
        
        Args:
            data: Search data to process
            
        Returns:
            dict: Processed search data
        """
        # Default implementation that should be overridden by subclasses
        return {
            'platform': self.platform,
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
        search_type = kwargs.get('search_type', 'posts')
        
        if search_type == 'profile':
            return self.get_profile(query)
        elif search_type == 'posts':
            return self.search_posts(query, kwargs.get('max_results', 100))
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
                'platform': self.platform,
                'data_type': 'unknown',
                'items': [],
                'raw_data': data
            }
            
            return True, processed_data, ""
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return False, None, f"Error processing data: {str(e)}"


class TwitterAdapter(SocialMediaAdapter):
    """Adapter for the Twitter API."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.platform = 'twitter'
    
    def test_connection(self):
        """Test the connection to the Twitter API."""
        # Use Twitter's rate limit status endpoint as a test
        endpoint = 'application/rate_limit_status'
        success, status_code, _, error_message = self._make_request('GET', endpoint)
        
        if success:
            return True, f"Twitter API connection successful with status {status_code}"
        else:
            return False, f"Twitter API connection failed: {error_message}"
    
    def process_profile_data(self, data):
        """Process Twitter profile data."""
        try:
            # Extract relevant fields from the Twitter profile
            processed = {
                'platform': self.platform,
                'username': data.get('screen_name', ''),
                'display_name': data.get('name', ''),
                'description': data.get('description', ''),
                'location': data.get('location', ''),
                'followers_count': data.get('followers_count', 0),
                'following_count': data.get('friends_count', 0),
                'tweets_count': data.get('statuses_count', 0),
                'created_at': data.get('created_at', ''),
                'verified': data.get('verified', False),
                'profile_image_url': data.get('profile_image_url_https', ''),
                'profile_url': f"https://twitter.com/{data.get('screen_name', '')}",
                'raw_data': data
            }
            return processed
        except Exception as e:
            logger.error(f"Error processing Twitter profile: {str(e)}")
            return {'platform': self.platform, 'error': str(e), 'raw_data': data}
    
    def process_search_data(self, data):
        """Process Twitter search data."""
        try:
            # Extract tweets from the search results
            tweets = data.get('statuses', [])
            processed = {
                'platform': self.platform,
                'count': len(tweets),
                'items': []
            }
            
            for tweet in tweets:
                processed_tweet = {
                    'id': tweet.get('id_str', ''),
                    'text': tweet.get('text', ''),
                    'created_at': tweet.get('created_at', ''),
                    'likes': tweet.get('favorite_count', 0),
                    'retweets': tweet.get('retweet_count', 0),
                    'user': {
                        'id': tweet.get('user', {}).get('id_str', ''),
                        'username': tweet.get('user', {}).get('screen_name', ''),
                        'display_name': tweet.get('user', {}).get('name', ''),
                        'verified': tweet.get('user', {}).get('verified', False)
                    },
                    'url': f"https://twitter.com/{tweet.get('user', {}).get('screen_name', '')}/status/{tweet.get('id_str', '')}"
                }
                processed['items'].append(processed_tweet)
            
            return processed
        except Exception as e:
            logger.error(f"Error processing Twitter search: {str(e)}")
            return {'platform': self.platform, 'error': str(e), 'raw_data': data}


class FacebookAdapter(SocialMediaAdapter):
    """Adapter for the Facebook Graph API."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.platform = 'facebook'
    
    def test_connection(self):
        """Test the connection to the Facebook API."""
        # Use Facebook's /me endpoint as a test
        endpoint = 'me'
        success, status_code, _, error_message = self._make_request('GET', endpoint)
        
        if success:
            return True, f"Facebook API connection successful with status {status_code}"
        else:
            return False, f"Facebook API connection failed: {error_message}"
    
    def process_profile_data(self, data):
        """Process Facebook profile data."""
        try:
            # Extract relevant fields from the Facebook profile
            processed = {
                'platform': self.platform,
                'id': data.get('id', ''),
                'username': data.get('username', ''),
                'name': data.get('name', ''),
                'about': data.get('about', ''),
                'category': data.get('category', ''),
                'fan_count': data.get('fan_count', 0),
                'website': data.get('website', ''),
                'profile_url': f"https://facebook.com/{data.get('id', '')}",
                'raw_data': data
            }
            return processed
        except Exception as e:
            logger.error(f"Error processing Facebook profile: {str(e)}")
            return {'platform': self.platform, 'error': str(e), 'raw_data': data}
    
    def process_search_data(self, data):
        """Process Facebook search data."""
        try:
            # Extract posts from the search results
            posts = data.get('data', [])
            processed = {
                'platform': self.platform,
                'count': len(posts),
                'items': []
            }
            
            for post in posts:
                processed_post = {
                    'id': post.get('id', ''),
                    'message': post.get('message', ''),
                    'created_time': post.get('created_time', ''),
                    'type': post.get('type', ''),
                    'url': f"https://facebook.com/{post.get('id', '')}"
                }
                
                # Add any attached media
                if 'attachments' in post:
                    processed_post['attachments'] = post['attachments'].get('data', [])
                
                processed['items'].append(processed_post)
            
            return processed
        except Exception as e:
            logger.error(f"Error processing Facebook search: {str(e)}")
            return {'platform': self.platform, 'error': str(e), 'raw_data': data}


class LinkedInAdapter(SocialMediaAdapter):
    """Adapter for the LinkedIn API."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.platform = 'linkedin'
    
    def test_connection(self):
        """Test the connection to the LinkedIn API."""
        # Use LinkedIn's /me endpoint as a test
        endpoint = 'me'
        success, status_code, _, error_message = self._make_request('GET', endpoint)
        
        if success:
            return True, f"LinkedIn API connection successful with status {status_code}"
        else:
            return False, f"LinkedIn API connection failed: {error_message}"
    
    def process_profile_data(self, data):
        """Process LinkedIn profile data."""
        try:
            # Extract relevant fields from the LinkedIn profile
            processed = {
                'platform': self.platform,
                'id': data.get('id', ''),
                'first_name': data.get('firstName', {}).get('localized', {}).get('en_US', ''),
                'last_name': data.get('lastName', {}).get('localized', {}).get('en_US', ''),
                'headline': data.get('headline', {}).get('localized', {}).get('en_US', ''),
                'industry': data.get('industry', {}).get('name', ''),
                'location': data.get('location', {}).get('preferredGeoPlace', {}).get('name', ''),
                'profile_url': f"https://linkedin.com/in/{data.get('vanityName', '')}",
                'raw_data': data
            }
            return processed
        except Exception as e:
            logger.error(f"Error processing LinkedIn profile: {str(e)}")
            return {'platform': self.platform, 'error': str(e), 'raw_data': data}
    
    def process_search_data(self, data):
        """Process LinkedIn search data."""
        try:
            # LinkedIn API doesn't provide a direct search for posts
            # This is a placeholder implementation
            processed = {
                'platform': self.platform,
                'count': 0,
                'items': [],
                'raw_data': data
            }
            
            return processed
        except Exception as e:
            logger.error(f"Error processing LinkedIn search: {str(e)}")
            return {'platform': self.platform, 'error': str(e), 'raw_data': data}