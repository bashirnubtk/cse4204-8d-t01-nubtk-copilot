from rest_framework import serializers
from apps.academics.models import StudentProfile

class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Global API entity data serializer mapping the centralized student model layer.
    """
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'student_name', 'digital_id', 'status', 
            'ssc_gpa', 'hsc_gpa', 'current_semester', 'current_cgpa',
            'class_test_mark', 'quiz_mark', 'attendance_percentage'
        ]
        read_only_fields = ['digital_id', 'status']