import os
from django.apps import AppConfig

class AiMentorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_mentor'
    # এই নিচের লাইনটি জ্যাংগোর ক্যাশ মেমোরি কনফ্লিক্ট পুরোপুরি দূর করে দেবে
    path = os.path.dirname(os.path.abspath(__file__))