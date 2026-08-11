from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from apps.academics.models import StudentProfile

def student_register_view(request):
    UserMD = get_user_model()
    if request.method == 'POST':
        name = request.POST.get('student_name')
        father = request.POST.get('father_name')
        mother = request.POST.get('mother_name')
        phone = request.POST.get('phone_number')
        email = request.POST.get('email')
        ssc = request.POST.get('ssc_gpa')
        hsc = request.POST.get('hsc_gpa')
        department = request.POST.get('department')
        profile_pic = request.FILES.get('profile_picture')

        if UserMD.objects.filter(email=email).exists():
            messages.error(request, "Registration rejected. This email address already exists.")
            return redirect('student_register')

        user = UserMD.objects.create_user(username=email, email=email, password="temp123", is_student=True)
        user.is_active = False
        user.save()

        profile = StudentProfile.objects.create(
            user=user, student_name=name, father_name=father, mother_name=mother,
            phone_number=phone, ssc_gpa=float(ssc) if ssc else 0.0, hsc_gpa=float(hsc) if hsc else 0.0,
            department=department, profile_picture=profile_pic, current_semester=1
        )
        messages.success(request, f"Application submitted! Your Enrollment ID is {profile.digital_id}.")
        return redirect('home')
    return render(request, 'dashboard/register.html')

def portal_login_view(request):
    if request.method == 'POST':
        email_input = request.POST.get('username')
        password_input = request.POST.get('password')
        UserMD = get_user_model()

        try:
            user = UserMD.objects.get(email=email_input)
        except UserMD.DoesNotExist:
            try:
                user = UserMD.objects.get(username=email_input)
            except UserMD.DoesNotExist:
                messages.error(request, "Authentication failed. Invalid email or ID.")
                return render(request, 'dashboard/login.html')

        if user.check_password(password_input):
            if getattr(user, 'is_student', False):
                if not hasattr(user, 'student_profile') or user.student_profile.status!= 'APPROVED':
                    messages.error(request, "Access denied. Profile pending review.")
                    return redirect('portal_login')
            login(request, user)
            return redirect('admin_dashboard' if (user.is_superuser or getattr(user, 'is_university_admin', False)) else 'student_dashboard')
        else:
            messages.error(request, "Authentication failed. Invalid email or password.")
    return render(request, 'dashboard/login.html')

def portal_logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('home')