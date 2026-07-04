# Auto-generated file
from rest_framework import serializers
from backend.apps.students.models import StudentProfile, SkillLog
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class SkillLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillLog
        fields = '__all__'

class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = SkillLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'student_id', 'department', 'current_cgpa', 'phone_number', 'github_profile', 'linkedin_profile', 'skills', 'created_at']