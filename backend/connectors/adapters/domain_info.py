"""
Adapter classes for domain information services.
"""

import logging
import re
from datetime import datetime
from .base import BaseAdapter

logger = logging.getLogger(__name__)


class DomainInfoAdapter(BaseAdapter):
    """Base class for domain information adapters with common functionality."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.service = None  # To be set by subclasses
    
    def get_domain_info(self, domain):
        """
        Get information about a domain.
        
        Args:
            domain: Domain name to look up
            
        Returns:
            tuple: (success, domain_data, error_message)
        """
        # Validate domain format
        if not self._is_valid_domain(domain):
            return False, None, f"Invalid domain format: {domain}"
        
        endpoint = self.configuration.get('domain_endpoint', 'domain/{domain}')
        endpoint = endpoint.format(domain=domain)
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint)
        
        if success:
            return True, self.process_domain_data(response_data), ""
        else:
            return False, None, error_message
    
    def _is_valid_domain(self, domain):
        """
        Check if a domain name has a valid format.
        
        Args:
            domain: Domain name to check
            
        Returns:
            bool: True if the domain format is valid, False otherwise
        """
        # Basic domain validation pattern
        pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))
    
    def process_domain_data(self, data):
        """
        Process domain data received from the API.
        
        Args:
            data: Domain data to process
            
        Returns:
            dict: Processed domain data
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
            query: Domain to search for
            **kwargs: Additional search parameters
            
        Returns:
            tuple: (success, results, error_message)
        """
        return self.get_domain_info(query)
    
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
                'data_type': 'domain_info',
                'raw_data': data
            }
            
            return True, processed_data, ""
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return False, None, f"Error processing data: {str(e)}"


class WhoisAdapter(DomainInfoAdapter):
    """Adapter for WHOIS services."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.service = 'whois'
    
    def test_connection(self):
        """Test the connection to the WHOIS service."""
        # Many WHOIS APIs require a domain parameter, so we'll use a well-known domain
        test_domain = 'example.com'
        success, _, _, error_message = self.get_domain_info(test_domain)
        
        if success:
            return True, f"WHOIS service connection successful"
        else:
            return False, f"WHOIS service connection failed: {error_message}"
    
    def process_domain_data(self, data):
        """Process WHOIS data."""
        try:
            # Extract relevant fields from the WHOIS data
            processed = {
                'service': self.service,
                'domain': data.get('domain', ''),
                'registrar': data.get('registrar', {}).get('name', ''),
                'registered_on': data.get('created_date', ''),
                'expires_on': data.get('expiration_date', ''),
                'updated_on': data.get('updated_date', ''),
                'status': data.get('status', []),
                'name_servers': data.get('name_servers', []),
                'raw_data': data
            }
            
            # Process registrant information if available
            if 'registrant' in data:
                registrant = data['registrant']
                processed['registrant'] = {
                    'name': registrant.get('name', ''),
                    'organization': registrant.get('organization', ''),
                    'email': registrant.get('email', ''),
                    'phone': registrant.get('phone', ''),
                    'country': registrant.get('country', ''),
                    'state': registrant.get('state', ''),
                    'city': registrant.get('city', '')
                }
            
            # Calculate age of domain
            if processed['registered_on']:
                try:
                    registered_date = datetime.fromisoformat(processed['registered_on'].replace('Z', '+00:00'))
                    now = datetime.now()
                    domain_age_days = (now - registered_date).days
                    processed['domain_age_days'] = domain_age_days
                except (ValueError, TypeError):
                    processed['domain_age_days'] = None
            
            return processed
        except Exception as e:
            logger.error(f"Error processing WHOIS data: {str(e)}")
            return {'service': self.service, 'error': str(e), 'raw_data': data}


class DNSAdapter(DomainInfoAdapter):
    """Adapter for DNS information services."""
    
    def __init__(self, connector):
        super().__init__(connector)
        self.service = 'dns'
    
    def test_connection(self):
        """Test the connection to the DNS service."""
        # Many DNS APIs require a domain parameter, so we'll use a well-known domain
        test_domain = 'example.com'
        success, _, _, error_message = self.get_domain_info(test_domain)
        
        if success:
            return True, f"DNS service connection successful"
        else:
            return False, f"DNS service connection failed: {error_message}"
    
    def get_domain_info(self, domain, record_type='ANY'):
        """
        Get DNS information for a domain.
        
        Args:
            domain: Domain name to look up
            record_type: Type of DNS record to lookup (A, MX, CNAME, TXT, etc.)
            
        Returns:
            tuple: (success, dns_data, error_message)
        """
        # Validate domain format
        if not self._is_valid_domain(domain):
            return False, None, f"Invalid domain format: {domain}"
        
        endpoint = self.configuration.get('dns_endpoint', 'dns/{domain}/{record_type}')
        endpoint = endpoint.format(domain=domain, record_type=record_type)
        
        success, status_code, response_data, error_message = self._make_request('GET', endpoint)
        
        if success:
            return True, self.process_domain_data(response_data), ""
        else:
            return False, None, error_message
    
    def process_domain_data(self, data):
        """Process DNS data."""
        try:
            # Extract DNS records by type
            records = {
                'A': [],
                'AAAA': [],
                'MX': [],
                'NS': [],
                'TXT': [],
                'CNAME': [],
                'SOA': []
            }
            
            if isinstance(data, dict) and 'records' in data:
                for record in data['records']:
                    record_type = record.get('type', '')
                    if record_type in records:
                        records[record_type].append(record)
            
            # Create a more structured output
            processed = {
                'service': self.service,
                'domain': data.get('domain', ''),
                'records': records,
                'raw_data': data
            }
            
            # Extract IP addresses
            processed['ip_addresses'] = [record.get('value', '') for record in records['A']]
            
            # Extract mail servers
            processed['mail_servers'] = [record.get('value', '') for record in records['MX']]
            
            # Extract name servers
            processed['name_servers'] = [record.get('value', '') for record in records['NS']]
            
            return processed
        except Exception as e:
            logger.error(f"Error processing DNS data: {str(e)}")
            return {'service': self.service, 'error': str(e), 'raw_data': data}
    
    def search(self, query, **kwargs):
        """
        Perform a search using the connector.
        
        Args:
            query: Domain to search for
            **kwargs: Additional search parameters
            
        Returns:
            tuple: (success, results, error_message)
        """
        record_type = kwargs.get('record_type', 'ANY')
        return self.get_domain_info(query, record_type)