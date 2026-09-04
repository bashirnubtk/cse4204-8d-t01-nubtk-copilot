from django.urls import path
from django.http import HttpResponse
from .views import student_register_view, student_login_view, student_logout_view

# আমরা পরবর্তীতে যে ড্যাশবোর্ড ভিউগুলো বানাবো, সেগুলোকে এখানে ডিক্লেয়ার করার জন্য জাস্ট নাম দিয়ে রাখছি
def temporary_student_dashboard(request):
    return HttpResponse("<h1>স্বাগতম স্টুডেন্ট ড্যাশবোর্ডে!</h1> <p>আপনার ডিজিটাল আইডি এবং এআই মেন্টর এখানে থাকবে।</p>")

def temporary_admin_dashboard(request):
    return HttpResponse("<h1>স্বাগতম অ্যাডমিন ড্যাশবোর্ডে!</h1> <p>এখান থেকে আপনি স্টুডেন্টের রেজাল্ট এবং পেমেন্ট এড করতে পারবেন।</p>")

urlpatterns = [
    # 🔐 অথেনটিকেশন রুটস (রেজিস্ট্রেশন, লগইন এবং লগআউট)
    path('register/', student_register_view, name='student_register'),
    path('login/', student_login_view, name='student_login'),
    path('logout/', student_logout_view, name='student_logout'),
    
    # 🔗 ড্যাশবোর্ড রুটস (স্মার্ট লগইন মেকানিজমকে সচল রাখবে)
    path('student-dashboard/', temporary_student_dashboard, name='student_dashboard'),
    path('admin-dashboard/', temporary_admin_dashboard, name='admin_dashboard'),
    
    # 🚀 আপনার আপডেটের ফিউচার ড্যাশবোর্ড প্লেসহোল্ডার (প্রয়োজন হলে ব্যবহার করতে পারবেন)
    path('dashboard/', lambda r: HttpResponse("Student Dashboard Coming Soon..."), name='student_dashboard_soon'),
]