# Auto-generated file
from rest_framework import viewsets
from backend.apps.students.models import StudentProfile
from backend.api.serializers.students import StudentProfileSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class StudentViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all().select_related('user').prefetch_related('skills')
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]