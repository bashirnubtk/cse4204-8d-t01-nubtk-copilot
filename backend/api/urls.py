from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.api.viewsets.students import StudentViewSet

router = DefaultRouter()
# Registering the core student endpoints
router.register(r'student-profiles', StudentViewSet, basename='student-profile')

urlpatterns = [
    path('', include(router.urls)),
]