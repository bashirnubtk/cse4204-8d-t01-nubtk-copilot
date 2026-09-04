from django.db import models
from apps.academics.models import StudentProfile

class AIMentorSession(models.Model):
    """
    Stores automated career guideline sessions matching active student profiles.
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='ai_mentor_sessions')
    query_text = models.TextField()
    response_text = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Session for {self.student.student_name} at {self.generated_at}"