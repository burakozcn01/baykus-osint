"""
Adapter classes for image analysis services.
"""

import logging
import base64
import re
from .base import BaseAdapter

logger = logging.getLogger(__name__)


class ImageAnalysisAdapter(BaseAdapter):
    """Base class for image analysis adapters with common functionality."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.service = None  # To be set by subclasses
    
    def analyze_image_url(self, image_url):
        """
        Analyze an image from a URL.
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            tuple: (success, analysis_results, error_message)
        """
        # Validate URL format
        if not self._is_valid_url(image_url):
            return False, None, f"Invalid URL format: {image_url}"
        
        endpoint = self.configuration.get('url_endpoint', 'analyze')
        params = {'url': image_url}
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint, params=params)
        
        if success:
            return True, self.process_analysis_results(response_data), ""
        else:
            return False, None, error_message
    
    def analyze_image_file(self, image_data, filename=None):
        """
        Analyze an image from file data.
        
        Args:
            image_data: Binary image data or base64 encoded string
            filename: Optional filename
            
        Returns:
            tuple: (success, analysis_results, error_message)
        """
        endpoint = self.configuration.get('file_endpoint', 'analyze')
        
        # Check if image_data is already a base64 string
        if isinstance(image_data, str):
            try:
                # Try to decode to check if it's valid base64
                base64.b64decode(image_data)
                base64_data = image_data
            except Exception:
                return False, None, "Invalid base64 encoded image data"
        else:
            # Convert binary data to base64
            try:
                base64_data = base64.b64encode(image_data).decode('utf-8')
            except Exception as e:
                return False, None, f"Error encoding image data: {str(e)}"
        
        # Prepare the request body
        body = {
            'image': base64_data
        }
        
        if filename:
            body['filename'] = filename
        
        success, status_code, response_data, error_message = self._make_request('POST', endpoint, data=body)
        
        if success:
            return True, self.process_analysis_results(response_data), ""
        else:
            return False, None, error_message
    
    def _is_valid_url(self, url):
        """
        Check if a URL has a valid format.
        
        Args:
            url: URL to check
            
        Returns:
            bool: True if the URL format is valid, False otherwise
        """
        # Basic URL validation pattern
        pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[-\w%!$&\'()*+,;=:@/~]+)*(?:\?[-\w%!$&\'()*+,;=:@/~]*)?(?:#[-\w%!$&\'()*+,;=:@/~]*)?$'
        return bool(re.match(pattern, url))
    
    def process_analysis_results(self, data):
        """
        Process image analysis results.
        
        Args:
            data: Analysis results to process
            
        Returns:
            dict: Processed analysis results
        """
        # Default implementation that should be overridden by subclasses
        return {
            'service': self.service,
            'raw_data': data
        }
    
    def search(self, query, **kwargs):
        """
        Perform a search using the connector.
        
        Args:
            query: URL or base64 image data
            **kwargs: Additional search parameters
            
        Returns:
            tuple: (success, results, error_message)
        """
        search_type = kwargs.get('search_type', 'url')
        
        if search_type == 'url':
            return self.analyze_image_url(query)
        elif search_type == 'file':
            filename = kwargs.get('filename')
            return self.analyze_image_file(query, filename)
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
            return True, self.process_analysis_results(data), ""
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return False, None, f"Error processing data: {str(e)}"


class ExifExtractorAdapter(ImageAnalysisAdapter):
    """Adapter for EXIF metadata extraction services."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.service = 'exif_extractor'
    
    def test_connection(self):
        """Test the connection to the EXIF extraction service."""
        # Use a well-known image URL as a test
        test_url = 'https://www.example.com/test.jpg'
        success, _, _, error_message = self.analyze_image_url(test_url)
        
        if success:
            return True, f"EXIF extraction service connection successful"
        else:
            return False, f"EXIF extraction service connection failed: {error_message}"
    
    def process_analysis_results(self, data):
        """Process EXIF extraction results."""
        try:
            exif_data = data.get('exif', {})
            
            processed = {
                'service': self.service,
                'type': 'exif_extraction',
                'filename': data.get('filename', ''),
                'mime_type': data.get('mime_type', ''),
                'file_size': data.get('file_size', 0),
                'width': data.get('width', 0),
                'height': data.get('height', 0),
                'has_exif': bool(exif_data),
                'raw_data': data
            }
            
            # Extract common EXIF fields
            if exif_data:
                exif = {}
                
                # Camera info
                if 'make' in exif_data or 'model' in exif_data:
                    exif['camera'] = {
                        'make': exif_data.get('make', ''),
                        'model': exif_data.get('model', ''),
                        'software': exif_data.get('software', '')
                    }
                
                # Location info
                if 'gps_latitude' in exif_data or 'gps_longitude' in exif_data:
                    exif['location'] = {
                        'latitude': exif_data.get('gps_latitude', None),
                        'longitude': exif_data.get('gps_longitude', None),
                        'altitude': exif_data.get('gps_altitude', None),
                        'location_name': exif_data.get('location_name', '')
                    }
                
                # Time info
                if 'date_time_original' in exif_data:
                    exif['time'] = {
                        'date_time_original': exif_data.get('date_time_original', ''),
                        'date_time_digitized': exif_data.get('date_time_digitized', ''),
                        'date_time': exif_data.get('date_time', '')
                    }
                
                # Photo info
                photo_info = {}
                if 'exposure_time' in exif_data:
                    photo_info['exposure_time'] = exif_data.get('exposure_time', '')
                if 'f_number' in exif_data:
                    photo_info['f_number'] = exif_data.get('f_number', '')
                if 'iso_speed_ratings' in exif_data:
                    photo_info['iso'] = exif_data.get('iso_speed_ratings', '')
                if 'focal_length' in exif_data:
                    photo_info['focal_length'] = exif_data.get('focal_length', '')
                
                if photo_info:
                    exif['photo_info'] = photo_info
                
                # Add all raw EXIF data
                exif['all'] = exif_data
                
                processed['exif'] = exif
            
            return processed
        except Exception as e:
            logger.error(f"Error processing EXIF extraction results: {str(e)}")
            return {'service': self.service, 'error': str(e), 'raw_data': data}


class ReverseImageSearchAdapter(ImageAnalysisAdapter):
    """Adapter for reverse image search services."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.service = 'reverse_image_search'
    
    def test_connection(self):
        """Test the connection to the reverse image search service."""
        # Use a well-known image URL as a test
        test_url = 'https://www.example.com/test.jpg'
        success, _, _, error_message = self.analyze_image_url(test_url)
        
        if success:
            return True, f"Reverse image search service connection successful"
        else:
            return False, f"Reverse image search service connection failed: {error_message}"
    
    def process_analysis_results(self, data):
        """Process reverse image search results."""
        try:
            matches = data.get('matches', [])
            
            processed = {
                'service': self.service,
                'type': 'reverse_image_search',
                'query_image': data.get('query_image', ''),
                'total_matches': len(matches),
                'matches': [],
                'raw_data': data
            }
            
            for match in matches:
                processed_match = {
                    'url': match.get('url', ''),
                    'title': match.get('title', ''),
                    'description': match.get('description', ''),
                    'website': match.get('website', ''),
                    'similarity_score': match.get('similarity_score', 0),
                    'thumbnail_url': match.get('thumbnail_url', ''),
                    'width': match.get('width', 0),
                    'height': match.get('height', 0)
                }
                
                processed['matches'].append(processed_match)
            
            # Sort matches by similarity score
            processed['matches'] = sorted(processed['matches'], key=lambda x: x['similarity_score'], reverse=True)
            
            return processed
        except Exception as e:
            logger.error(f"Error processing reverse image search results: {str(e)}")
            return {'service': self.service, 'error': str(e), 'raw_data': data}