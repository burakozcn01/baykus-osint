from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Asset, ScanResult, Relationship


@receiver(post_save, sender=Asset)
def log_asset_created(sender, instance, created, **kwargs):
    """Log when a new asset is created."""
    if created:
        # Here we could create an alert or activity log entry
        pass


@receiver(post_save, sender=ScanResult)
def process_scan_result(sender, instance, created, **kwargs):
    """Process a scan result when it is updated."""
    if not created and instance.status == 'completed':
        # Here we could trigger analysis of the scan results
        # For example, creating alerts for significant findings
        pass


@receiver([post_save, post_delete], sender=Asset)
def update_target_asset_count(sender, instance, **kwargs):
    """Update the target's asset count when an asset is created, updated, or deleted."""
    # This is an example of how we could track asset counts per target
    # We might store this in a cached field on the Target model
    pass


@receiver(post_save, sender=Relationship)
def process_new_relationship(sender, instance, created, **kwargs):
    """Process a new relationship when it is created."""
    if created:
        # Here we could update related assets or create alerts
        pass