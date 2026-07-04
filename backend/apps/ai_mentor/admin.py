from django.contrib import admin
from .models import AIMentorSession

class AIMentorSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'generated_at']
    search_fields = ['student__student_name', 'query_text']

admin.site.register(AIMentorSession, AIMentorSessionAdmin)