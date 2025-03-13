from django.apps import AppConfig


class ConnectorsConfig(AppConfig):
    """Configuration for the connectors app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'connectors'
    
    def ready(self):
        """Import signals when the app is ready."""
        import connectors.signals