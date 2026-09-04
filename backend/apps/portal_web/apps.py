from django.apps import AppConfig

class PortalWebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Defining the absolute internal object path for Django registry
    name = 'apps.portal_web'