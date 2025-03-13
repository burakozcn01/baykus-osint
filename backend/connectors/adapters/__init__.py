"""
This module provides adapter classes for different connector types.
Each adapter type implements the methods defined in the BaseAdapter class.
"""

from .base import BaseAdapter
from .social_media import TwitterAdapter, FacebookAdapter, LinkedInAdapter
from .domain_info import WhoisAdapter, DNSAdapter
from .search_engine import GoogleAdapter, BingAdapter
from .email_verify import EmailVerificationAdapter
from .pastebin import PastebinAdapter
from .username_search import UsernameSearchAdapter
from .image_analysis import ExifExtractorAdapter, ReverseImageSearchAdapter

# Mapping of connector types to their adapter classes
CONNECTOR_TYPE_ADAPTERS = {
    'social_media': {
        'twitter': TwitterAdapter,
        'facebook': FacebookAdapter,
        'linkedin': LinkedInAdapter,
    },
    'domain_info': {
        'whois': WhoisAdapter,
        'dns': DNSAdapter,
    },
    'search_engine': {
        'google': GoogleAdapter,
        'bing': BingAdapter,
    },
    'email_verify': {
        'default': EmailVerificationAdapter,
    },
    'pastebin': {
        'default': PastebinAdapter,
    },
    'username_search': {
        'default': UsernameSearchAdapter,
    },
    'image_analysis': {
        'exif': ExifExtractorAdapter,
        'reverse_search': ReverseImageSearchAdapter,
    },
}


def get_adapter_for_connector(connector):
    """
    Get the appropriate adapter for a connector.
    
    Args:
        connector: The Connector model instance
        
    Returns:
        An instance of the appropriate adapter class, or None if no adapter is available
    """
    connector_type = connector.connector_type
    
    # Check if we have adapters for this connector type
    if connector_type not in CONNECTOR_TYPE_ADAPTERS:
        return None
    
    # Get the specific adapter based on the connector configuration or name
    adapter_map = CONNECTOR_TYPE_ADAPTERS[connector_type]
    
    # Try to get a specific adapter from the connector's configuration
    adapter_key = connector.configuration.get('adapter_key', 'default')
    
    # If the adapter_key isn't in our mapping, fall back to 'default'
    if adapter_key not in adapter_map and 'default' in adapter_map:
        adapter_key = 'default'
    
    # If we still don't have a valid adapter key, use the first one available
    if adapter_key not in adapter_map and adapter_map:
        adapter_key = next(iter(adapter_map))
    
    # If we have a valid adapter, instantiate and return it
    if adapter_key in adapter_map:
        adapter_class = adapter_map[adapter_key]
        return adapter_class(connector)
    
    return None