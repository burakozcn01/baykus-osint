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
        

class InstagramAdapter(SocialMediaAdapter):
    """Adapter for the Instagram API."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.platform = 'instagram'
    
    def test_connection(self):
        """Test the connection to the Instagram API."""
        endpoint = 'users/self'
        success, status_code, _, error_message = self._make_request('GET', endpoint)
        
        if success:
            return True, f"Instagram API connection successful with status {status_code}"
        else:
            return False, f"Instagram API connection failed: {error_message}"
    
    def process_profile_data(self, data):
        """Process Instagram profile data."""
        try:
            processed = {
                'platform': self.platform,
                'id': data.get('id', ''),
                'username': data.get('username', ''),
                'full_name': data.get('full_name', ''),
                'biography': data.get('biography', ''),
                'followers_count': data.get('follower_count', 0),
                'following_count': data.get('following_count', 0),
                'media_count': data.get('media_count', 0),
                'is_private': data.get('is_private', False),
                'is_verified': data.get('is_verified', False),
                'profile_pic_url': data.get('profile_pic_url', ''),
                'profile_url': f"https://instagram.com/{data.get('username', '')}",
                'raw_data': data
            }
            return processed
        except Exception as e:
            logger.error(f"Error processing Instagram profile: {str(e)}")
            return {'platform': self.platform, 'error': str(e), 'raw_data': data}
    
    def process_search_data(self, data):
        """Process Instagram search data."""
        try:
            media = data.get('items', [])
            processed = {
                'platform': self.platform,
                'count': len(media),
                'items': []
            }
            
            for item in media:
                processed_item = {
                    'id': item.get('id', ''),
                    'type': item.get('media_type', ''),
                    'caption': item.get('caption', {}).get('text', '') if item.get('caption') else '',
                    'created_time': item.get('created_time', ''),
                    'likes_count': item.get('like_count', 0),
                    'comments_count': item.get('comment_count', 0),
                    'user': {
                        'id': item.get('user', {}).get('id', ''),
                        'username': item.get('user', {}).get('username', ''),
                        'full_name': item.get('user', {}).get('full_name', '')
                    },
                    'url': f"https://instagram.com/p/{item.get('code', '')}"
                }
                processed['items'].append(processed_item)
            
            return processed
        except Exception as e:
            logger.error(f"Error processing Instagram search: {str(e)}")
            return {'platform': self.platform, 'error': str(e), 'raw_data': data}


class RedditAdapter(SocialMediaAdapter):
    """Adapter for the Reddit API."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.platform = 'reddit'
    
    def test_connection(self):
        """Test the connection to the Reddit API."""
        endpoint = 'api/v1/me'
        success, status_code, _, error_message = self._make_request('GET', endpoint)
        
        if success:
            return True, f"Reddit API connection successful with status {status_code}"
        else:
            return False, f"Reddit API connection failed: {error_message}"
    
    def _get_headers(self):
        """Get headers for Reddit API requests."""
        headers = super()._get_headers()
        
        # Reddit API requires a User-Agent with app name, version and username
        headers['User-Agent'] = f"Baykus OSINT Tool/1.0 (by /u/{self.configuration.get('reddit_username', 'baykus-osint')})"
        
        return headers
    
    def process_profile_data(self, data):
        """Process Reddit profile data."""
        try:
            processed = {
                'platform': self.platform,
                'id': data.get('id', ''),
                'username': data.get('name', ''),
                'created_utc': data.get('created_utc', 0),
                'comment_karma': data.get('comment_karma', 0),
                'link_karma': data.get('link_karma', 0),
                'is_gold': data.get('is_gold', False),
                'is_mod': data.get('is_mod', False),
                'has_verified_email': data.get('has_verified_email', False),
                'profile_url': f"https://reddit.com/user/{data.get('name', '')}",
                'raw_data': data
            }
            return processed
        except Exception as e:
            logger.error(f"Error processing Reddit profile: {str(e)}")
            return {'platform': self.platform, 'error': str(e), 'raw_data': data}
    
    def process_search_data(self, data):
        """Process Reddit search data."""
        try:
            if 'data' in data and 'children' in data['data']:
                items = data['data']['children']
                processed = {
                    'platform': self.platform,
                    'count': len(items),
                    'items': []
                }
                
                for item in items:
                    item_data = item.get('data', {})
                    kind = item.get('kind', '')
                    
                    if kind == 't3':  # Post
                        processed_item = {
                            'id': item_data.get('id', ''),
                            'type': 'post',
                            'title': item_data.get('title', ''),
                            'selftext': item_data.get('selftext', ''),
                            'created_utc': item_data.get('created_utc', 0),
                            'score': item_data.get('score', 0),
                            'upvote_ratio': item_data.get('upvote_ratio', 0),
                            'num_comments': item_data.get('num_comments', 0),
                            'subreddit': item_data.get('subreddit', ''),
                            'author': item_data.get('author', ''),
                            'url': f"https://reddit.com{item_data.get('permalink', '')}"
                        }
                    elif kind == 't1':  # Comment
                        processed_item = {
                            'id': item_data.get('id', ''),
                            'type': 'comment',
                            'body': item_data.get('body', ''),
                            'created_utc': item_data.get('created_utc', 0),
                            'score': item_data.get('score', 0),
                            'author': item_data.get('author', ''),
                            'subreddit': item_data.get('subreddit', ''),
                            'url': f"https://reddit.com{item_data.get('permalink', '')}"
                        }
                    else:
                        processed_item = {
                            'id': item_data.get('id', ''),
                            'type': 'unknown',
                            'raw_data': item_data
                        }
                    
                    processed['items'].append(processed_item)
                
                return processed
            else:
                return {'platform': self.platform, 'error': 'Invalid response format', 'raw_data': data}
        except Exception as e:
            logger.error(f"Error processing Reddit search: {str(e)}")
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