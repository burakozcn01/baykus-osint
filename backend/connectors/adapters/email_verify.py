"""
Adapter class for email verification services.
"""

import logging
import re
from .base import BaseAdapter

logger = logging.getLogger(__name__)


class EmailVerificationAdapter(BaseAdapter):
    """Adapter for email verification services."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.service = 'email_verify'
    
    def test_connection(self):
        """Test the connection to the email verification service."""
        # Use a well-known email as a test
        test_email = 'test@example.com'
        success, _, _, error_message = self.verify_email(test_email)
        
        if success:
            return True, f"Email verification service connection successful"
        else:
            return False, f"Email verification service connection failed: {error_message}"
    
    def verify_email(self, email):
        """
        Verify an email address.
        
        Args:
            email: Email address to verify
            
        Returns:
            tuple: (success, verification_data, error_message)
        """
        # Validate email format
        if not self._is_valid_email(email):
            return False, None, f"Invalid email format: {email}"
        
        endpoint = self.configuration.get('verify_endpoint', 'verify')
        params = {'email': email}
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint, params=params)
        
        if success:
            return True, self.process_verification_data(response_data), ""
        else:
            return False, None, error_message
    
    def _is_valid_email(self, email):
        """
        Check if an email address has a valid format.
        
        Args:
            email: Email address to check
            
        Returns:
            bool: True if the email format is valid, False otherwise
        """
        # Basic email validation pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def process_verification_data(self, data):
        """
        Process email verification data.
        
        Args:
            data: Verification data to process
            
        Returns:
            dict: Processed verification data
        """
        try:
            # Extract relevant fields from the verification data
            processed = {
                'service': self.service,
                'email': data.get('email', ''),
                'is_valid': data.get('is_valid', False),
                'is_disposable': data.get('is_disposable', False),
                'is_role_account': data.get('is_role_account', False),
                'domain': data.get('domain', ''),
                'domain_age_days': data.get('domain_age_days', 0),
                'mx_records': data.get('mx_records', []),
                'smtp_check': data.get('smtp_check', False),
                'raw_data': data
            }
            
            # Calculate a confidence score
            confidence_score = 0
            if processed['is_valid']:
                confidence_score += 0.3
            if not processed['is_disposable']:
                confidence_score += 0.2
            if not processed['is_role_account']:
                confidence_score += 0.1
            if processed['domain_age_days'] > 365:
                confidence_score += 0.2
            if processed['mx_records']:
                confidence_score += 0.1
            if processed['smtp_check']:
                confidence_score += 0.1
            
            processed['confidence_score'] = min(confidence_score, 1.0)
            
            return processed
        except Exception as e:
            logger.error(f"Error processing email verification data: {str(e)}")
            return {'service': self.service, 'error': str(e), 'raw_data': data}
    
    def search(self, query, **kwargs):
        """
        Perform a search using the connector.
        
        Args:
            query: Email address to verify
            **kwargs: Additional search parameters
            
        Returns:
            tuple: (success, results, error_message)
        """
        return self.verify_email(query)
    
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
                'data_type': 'email_verification',
                'raw_data': data
            }
            
            return True, processed_data, ""
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return False, None, f"Error processing data: {str(e)}"