from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserActivity

User = get_user_model()


@receiver(post_save, sender=User)
def log_user_created(sender, instance, created, **kwargs):
    """Log when a new user is created."""
    if created:
        UserActivity.objects.create(
            user=instance,
            activity_type='registration',
            description='User account created'
        )