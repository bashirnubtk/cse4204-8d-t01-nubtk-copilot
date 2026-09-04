from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.academics.models import StudentProfile

# Legacy triggers are preserved smoothly using the centralized academics infrastructure.
@receiver(post_save, sender=StudentProfile)
def student_profile_sync_callback(sender, instance, created, **kwargs):
    """
    Placeholder routing callback infrastructure ready for future API synchronization vectors.
    """
    pass