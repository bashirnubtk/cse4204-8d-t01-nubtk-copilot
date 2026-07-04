from django.contrib import admin
from .models import MLPerformancePrediction

class MLPerformancePredictionAdmin(admin.ModelAdmin):
    list_display = ['student', 'predicted_cgpa', 'readiness_score', 'updated_at']

admin.site.register(MLPerformancePrediction, MLPerformancePredictionAdmin)