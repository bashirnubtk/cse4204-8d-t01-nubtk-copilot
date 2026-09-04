from django.apps import AppConfig

class StudentsConfig(AppConfig):
    """
    Application registry manager for the students sub-module.
    Centralized configurations are mapped cleanly without triggering legacy system signals.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.students'

    def ready(self):
        # Legacy signals import has been removed to isolate structural dependency issues.
        pass