from django.urls import path
from. import views, auth_views, admin_views, ai_views, student_views
from. import utils

urlpatterns = [
    path('', views.home_view, name='home'),
    path('portal/admission/apply/', auth_views.student_register_view, name='student_register'),
    path('portal/gateway/login/', auth_views.portal_login_view, name='portal_login'),
    path('portal-admin/login/', auth_views.portal_login_view, name='admin_login'),
    path('portal/gateway/logout/', auth_views.portal_logout_view, name='logout'),

    # Student - এখন student_views থেকে
    path('portal/student/dashboard/', student_views.student_dashboard_view, name='student_dashboard'),
    path('student-portal/payment/process/<int:payment_id>/', student_views.process_student_payment_gate, name='process_student_payment'),
    path('student-portal/resources/', student_views.student_resource_hub_view, name='student_resource_hub'),
    path('student-portal/resources/download/<int:resource_id>/', student_views.track_resource_click_view, name='track_resource_click'),

    # AI Chat
    path('student-portal/ai-chat-hub/', ai_views.student_ai_chat_hub_view, name='student_ai_chat_hub'),

    # Admin
    path('portal-admin/dashboard/', admin_views.admin_dashboard_view, name='admin_dashboard'),
    path('portal-admin/approve/<int:profile_id>/', admin_views.admin_approve_student_view, name='admin_approve_student'),
    path('portal-admin/reject/<int:profile_id>/', admin_views.admin_reject_student_view, name='admin_reject_student'),
    path('portal-admin/update-marks/<int:profile_id>/', admin_views.admin_update_marks_view, name='admin_update_marks'),
    path('portal-admin/delete/<int:profile_id>/', admin_views.admin_delete_student_view, name='admin_delete_student'),
    path('portal-admin/courses/', admin_views.admin_course_matrix_view, name='admin_course_matrix'),
    path('portal-admin/ai-analytics/', admin_views.admin_ai_analytics_view, name='admin_ai_analytics'),
    path('portal-admin/logout/', admin_views.admin_logout_view, name='admin_logout'),
    path('portal-admin/seed-curriculum/', admin_views.seed_cse_curriculum_view, name='seed_curriculum'),

    # PDF Utils
    path('student-portal/identity/download-pdf/', utils.export_digital_id_pdf_view, name='download_digital_id'),
    path('student-portal/payment/receipt/<int:payment_id>/', utils.export_payment_receipt_pdf_view, name='download_payment_receipt'),

    # Resource Hub aliases - পুরনো টেমপ্লেট ভাঙবে না
    path('admin-portal/resources/', admin_views.admin_manage_resources_view, name='admin_manage_resources'),
    path('student-portal/resource-hub/', student_views.student_resource_hub_view, name='student_resource_hub_alt'),
    path('student-portal/resource/click/<int:resource_id>/', student_views.track_resource_click_view, name='resource_click_tracker'),

    # Practical Skills
    path('student-portal/practical-skills/', student_views.student_practical_skills_view, name='student_practical_skills'),
]