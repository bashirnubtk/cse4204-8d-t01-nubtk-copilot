from django.db import models
from apps.academics.models import StudentProfile

class MLPerformancePrediction(models.Model):
    """
    Stores calculated industry readiness and scoring projections.
    """
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='ml_prediction')
    predicted_cgpa = models.FloatField(default=0.0)
    readiness_score = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prediction for {self.student.student_name}"

class AIChatSession(models.Model):
    """
    পয়েন্ট ৭.১: স্টুডেন্ট ও এআই-এর মধ্যকার রিয়েল-টাইম কনভারসেশন হিস্ট্রি সেভ রাখার টেবিল
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='chat_history')
    user_message = models.TextField()
    ai_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "AI Chat Session"
        verbose_name_plural = "AI Chat Sessions"

    def __str__(self):
        return f"Chat by {self.student.student_name} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"