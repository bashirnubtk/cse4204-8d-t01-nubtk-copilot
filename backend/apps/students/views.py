from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.utils.crypto import get_random_string
from .models import StudentProfile

User = get_user_model()

def student_register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        full_name = request.POST.get('full_name', '').strip()

        if User.objects.filter(email=email).exists():
            messages.error(request, "এই জিমেইলটি দিয়ে ইতিপূর্বে রেজিস্ট্রেশন করা হয়েছে। অন্য ইমেইল ব্যবহার করুন।")
            return redirect('student_register')

        generated_password = get_random_string(length=10)

        try:
            user = User.objects.create_user(username=email, email=email, password=generated_password)
            user.first_name = full_name.split()[0] if full_name else ''
            user.save()

            # প্রোফাইল তৈরি (যদি না থাকে)
            if not hasattr(user, 'student_profile'):
                StudentProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    father_name=request.POST.get('father_name', 'N/A'),
                    mother_name=request.POST.get('mother_name', 'N/A'),
                    phone_number=request.POST.get('phone', '0000000000'),
                    department=request.POST.get('department', 'CSE'),
                    ssc_gpa=float(request.POST.get('ssc_gpa')) if request.POST.get('ssc_gpa') else None,
                    hsc_gpa=float(request.POST.get('hsc_gpa')) if request.POST.get('hsc_gpa') else None,
                )

            messages.success(request, f"রেজিস্ট্রেশন সফল! পাসওয়ার্ড: {generated_password}")
            return redirect('student_login')

        except Exception as e:
            messages.error(request, f"রেজিস্ট্রেশনে সমস্যা: {str(e)}")
            return redirect('student_register')

    return render(request, 'dashboard/register.html')


def student_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "লগইন সফল হয়েছে!")
            return redirect('portal_web:student_dashboard')
        else:
            messages.error(request, "ভুল ইমেইল অথবা পাসওয়ার্ড!")

    return render(request, 'dashboard/login.html')


def student_logout_view(request):
    logout(request)
    messages.info(request, "লগআউট সফল হয়েছে।")
    return redirect('student_login')