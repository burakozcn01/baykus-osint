"""
Adapter class for phone number analysis services.
"""

import logging
import re
from .base import BaseAdapter

logger = logging.getLogger(__name__)


class PhoneAnalysisAdapter(BaseAdapter):
    """Adapter for phone number analysis services."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.service = 'phone_analysis'
    
    def test_connection(self):
        """Test the connection to the phone analysis service."""
        # Use a test phone number
        test_phone = '+12025550198'  # Example US number (not real)
        success, _, _, error_message = self.analyze_phone(test_phone)
        
        if success:
            return True, f"Phone analysis service connection successful"
        else:
            return False, f"Phone analysis service connection failed: {error_message}"
    
    def analyze_phone(self, phone_number):
        """
        Analyze a phone number.
        
        Args:
            phone_number: Phone number to analyze
            
        Returns:
            tuple: (success, analysis_data, error_message)
        """
        # Validate phone number format
        if not self._is_valid_phone(phone_number):
            return False, None, f"Invalid phone number format: {phone_number}"
        
        endpoint = self.configuration.get('analyze_endpoint', 'analyze')
        params = {'phone': phone_number}
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint, params=params)
        
        if success:
            return True, self.process_analysis_data(response_data), ""
        else:
            return False, None, error_message
    
    def _is_valid_phone(self, phone_number):
        """
        Check if a phone number has a valid format.
        
        Args:
            phone_number: Phone number to check
            
        Returns:
            bool: True if the phone number format is valid, False otherwise
        """
        # Basic international phone number validation pattern
        pattern = r'^\+?[0-9]{1,3}[-.\s]?[0-9]{1,14}$'
        return bool(re.match(pattern, phone_number))
    
    def process_analysis_data(self, data):
        """
        Process phone analysis data.
        
        Args:
            data: Analysis data to process
            
        Returns:
            dict: Processed analysis data
        """
        try:
            # Extract relevant fields from the phone analysis data
            processed = {
                'service': self.service,
                'phone_number': data.get('phone_number', ''),
                'formatted': data.get('formatted', ''),
                'country_code': data.get('country_code', ''),
                'country_name': data.get('country_name', ''),
                'location': data.get('location', ''),
                'carrier': data.get('carrier', ''),
                'line_type': data.get('line_type', ''),
                'valid': data.get('valid', False),
                'possible': data.get('possible', False),
                'raw_data': data
            }
            
            return processed
        except Exception as e:
            logger.error(f"Error processing phone analysis data: {str(e)}")
            return {'service': self.service, 'error': str(e), 'raw_data': data}
    
    def search(self, query, **kwargs):
        """
        Perform a search using the connector.
        
        Args:
            query: Phone number to analyze
            **kwargs: Additional search parameters
            
        Returns:
            tuple: (success, results, error_message)
        """
        return self.analyze_phone(query)
    
    def process_data(self, data):
        """
        Process data received from the connector.
        
        Args:
            data: Data to process
            
        Returns:
            tuple: (success, processed_data, error_message)
        """
        try:
            processed_data = {
                'service': self.service,
                'data_type': 'phone_analysis',
                'raw_data': data
            }
            
            return True, processed_data, ""
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return False, None, f"Error processing data: {str(e)}"