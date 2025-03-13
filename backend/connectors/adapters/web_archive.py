"""
Adapter class for web archive services like Wayback Machine.
"""

import logging
from datetime import datetime
from .base import BaseAdapter

logger = logging.getLogger(__name__)


class WebArchiveAdapter(BaseAdapter):
    """Base class for web archive adapters with common functionality."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.service = None  # To be set by subclasses
    
    def get_snapshots(self, url, from_date=None, to_date=None):
        """
        Get archive snapshots for a URL.
        
        Args:
            url: URL to search for
            from_date: Starting date (YYYYMMDD format or datetime)
            to_date: Ending date (YYYYMMDD format or datetime)
            
        Returns:
            tuple: (success, snapshots_data, error_message)
        """
        endpoint = self.configuration.get('snapshots_endpoint', 'snapshots')
        
        params = {'url': url}
        
        if from_date:
            if isinstance(from_date, datetime):
                from_date = from_date.strftime('%Y%m%d')
            params['from'] = from_date
            
        if to_date:
            if isinstance(to_date, datetime):
                to_date = to_date.strftime('%Y%m%d')
            params['to'] = to_date
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint, params=params)
        
        if success:
            return True, self.process_snapshots_data(response_data), ""
        else:
            return False, None, error_message
    
    def process_snapshots_data(self, data):
        """
        Process snapshots data.
        
        Args:
            data: Snapshots data to process
            
        Returns:
            dict: Processed snapshots data
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
            query: URL to search for
            **kwargs: Additional search parameters
            
        Returns:
            tuple: (success, results, error_message)
        """
        search_type = kwargs.get('search_type', 'snapshots')
        
        if search_type == 'snapshots':
            from_date = kwargs.get('from_date')
            to_date = kwargs.get('to_date')
            return self.get_snapshots(query, from_date, to_date)
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
            # Check if this is snapshot data
            if 'snapshots' in data:
                return True, self.process_snapshots_data(data), ""
            else:
                return True, {'service': self.service, 'raw_data': data}, ""
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return False, None, f"Error processing data: {str(e)}"


class WaybackMachineAdapter(WebArchiveAdapter):
    """Adapter for the Internet Archive's Wayback Machine."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.service = 'wayback_machine'
    
    def test_connection(self):
        """Test the connection to the Wayback Machine API."""
        test_url = 'example.com'
        success, _, _, error_message = self.get_snapshots(test_url, limit=1)
        
        if success:
            return True, f"Wayback Machine API connection successful"
        else:
            return False, f"Wayback Machine API connection failed: {error_message}"
    
    def get_snapshots(self, url, from_date=None, to_date=None, limit=None):
        """
        Get Wayback Machine snapshots for a URL.
        
        Args:
            url: URL to search for
            from_date: Starting date (YYYYMMDD format or datetime)
            to_date: Ending date (YYYYMMDD format or datetime)
            limit: Maximum number of snapshots to return
            
        Returns:
            tuple: (success, snapshots_data, error_message)
        """
        endpoint = self.configuration.get('cdx_endpoint', 'cdx/search')
        
        params = {
            'url': url,
            'output': 'json',
            'fl': 'timestamp,original,mimetype,statuscode,length',
            'collapse': 'timestamp:8'  # Group by day
        }
        
        if from_date:
            if isinstance(from_date, datetime):
                from_date = from_date.strftime('%Y%m%d')
            params['from'] = from_date
            
        if to_date:
            if isinstance(to_date, datetime):
                to_date = to_date.strftime('%Y%m%d')
            params['to'] = to_date
            
        if limit:
            params['limit'] = limit
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint, params=params)
        
        if success:
            return True, self.process_snapshots_data(response_data), ""
        else:
            return False, None, error_message
    
    def process_snapshots_data(self, data):
        """Process Wayback Machine snapshots data."""
        try:
            # Check if we have header data
            if not data or len(data) < 2:
                return {'service': self.service, 'error': 'No snapshot data found', 'raw_data': data}
            
            # Extract header and snapshots
            header = data[0]
            snapshots_data = data[1:]
            
            processed = {
                'service': self.service,
                'url': None,  # Will be extracted from snapshots
                'total_snapshots': len(snapshots_data),
                'snapshots': []
            }
            
            for snapshot in snapshots_data:
                if len(snapshot) < len(header):
                    continue
                
                snapshot_dict = dict(zip(header, snapshot))
                
                processed_snapshot = {
                    'timestamp': snapshot_dict.get('timestamp', ''),
                    'url': snapshot_dict.get('original', ''),
                    'mime_type': snapshot_dict.get('mimetype', ''),
                    'status_code': snapshot_dict.get('statuscode', ''),
                    'length': snapshot_dict.get('length', ''),
                    'archive_url': f"https://web.archive.org/web/{snapshot_dict.get('timestamp', '')}/{snapshot_dict.get('original', '')}"
                }
                
                processed['snapshots'].append(processed_snapshot)
                
                # Set the URL from the first snapshot if not set yet
                if not processed['url'] and snapshot_dict.get('original'):
                    processed['url'] = snapshot_dict['original']
            
            # Sort snapshots by timestamp (newest first)
            processed['snapshots'] = sorted(processed['snapshots'], key=lambda x: x['timestamp'], reverse=True)
            
            return processed
        except Exception as e:
            logger.error(f"Error processing Wayback Machine snapshots: {str(e)}")
            return {'service': self.service, 'error': str(e), 'raw_data': data} 