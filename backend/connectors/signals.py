from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Connector, ConnectorRequest


@receiver(post_save, sender=Connector)
def log_connector_created(sender, instance, created, **kwargs):
    """Log when a new connector is created."""
    if created:
        # Here we could create an activity log entry
        pass


@receiver(post_save, sender=ConnectorRequest)
def process_connector_request_result(sender, instance, created, **kwargs):
    """Process the result of a connector request."""
    if not created and instance.status == 'success':
        # Here we could trigger additional processing based on the request result
        # For example, updating rate limit information if we received a 429 status code
        if instance.status_code == 429:  # Too Many Requests
            connector = instance.connector
            connector.status = 'rate_limited'
            connector.save(update_fields=['status'])
    elif not created and instance.status == 'error':
        # We might want to update the connector status if we consistently get errors
        # This would be more sophisticated in a real implementation, involving counting errors
        pass