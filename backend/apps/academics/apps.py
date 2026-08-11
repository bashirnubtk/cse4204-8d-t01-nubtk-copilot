from django.apps import AppConfig

class AcademicsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Defining the absolute internal object path for Django registry
    name = 'apps.academics'