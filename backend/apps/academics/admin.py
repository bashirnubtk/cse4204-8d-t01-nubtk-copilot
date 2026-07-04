from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, Course, StudentResult, PaymentHistory, ResourceHub

# 1. Custom User Admin Setup
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_student', 'is_university_admin', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)

# 2. Student Profile Admin Setup
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('digital_id', 'student_name', 'department', 'current_semester', 'status', 'current_cgpa')
    list_filter = ('status', 'department', 'current_semester')
    search_fields = ('student_name', 'digital_id', 'phone_number')
    readonly_fields = ('digital_id', 'admission_score_percentage')

# 3. Course Admin Setup (FIXED: 'course_title' changed to 'course_name')
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'course_name', 'credits', 'semester', 'department')
    list_filter = ('semester', 'department')
    search_fields = ('course_code', 'course_name')

# 4. Student Result Admin Setup
@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ('student_profile', 'course', 'semester', 'subject_cgpa')
    list_filter = ('semester', 'course__department')
    search_fields = ('student_profile__student_name', 'course__course_code')

# 5. Payment History Admin Setup
@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('student_profile', 'semester', 'title', 'amount', 'status', 'due_date')
    list_filter = ('status', 'semester')
    search_fields = ('student_profile__student_name', 'title')

# 6. Resource Hub Admin Setup
@admin.register(ResourceHub)
class ResourceHubAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_by', 'click_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description')