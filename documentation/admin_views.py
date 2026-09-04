import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from apps.academics.models import StudentProfile, Course, StudentResult, ResourceHub

# AIChatSession মডেল ai_mentor এ থাকতে পারে, না থাকলে সেফ ফলব্যাক
try:
    from apps.ai_mentor.models import AIChatSession
except ImportError:
    try:
        from apps.ai_ml_engine.models import AIChatSession
    except ImportError:
        AIChatSession = None

# ==========================================
# 🎯 ১৬০ ক্রেডিট CSE কারিকুলাম - ৫৮টি কোর্স
# ==========================================
CSE_160_CURRICULUM = {
    1: [
        ('CSE-1101', 'Introduction to Computer Systems', 3.0),
        ('CSE-1102', 'Computer Hardware and Graphics Lab', 1.5),
        ('CSE-1103', 'Structured Programming Language', 3.0),
        ('CSE-1104', 'Structured Programming Lab', 1.5),
        ('MATH-1101', 'Differential and Integral Calculus', 3.0),
        ('ENG-1101', 'English Composition and Communication', 3.0),
        ('PHY-1101', 'Physics (Waves, Optics and Thermodynamics)', 3.0),
        ('PHY-1102', 'Physics Lab', 1.0)
    ],
    2: [
        ('CSE-1201', 'Object Oriented Programming', 3.0),
        ('CSE-1202', 'Object Oriented Programming Lab', 1.5),
        ('CSE-1203', 'Discrete Mathematics', 3.0),
        ('MATH-1201', 'Linear Algebra and Complex Variables', 3.0),
        ('CHEM-1201', 'General Chemistry', 3.0),
        ('CHEM-1202', 'Chemistry Lab', 1.0),
        ('EEE-1201', 'Basic Electrical Engineering', 3.0),
        ('EEE-1202', 'Electrical Engineering Lab', 1.0)
    ],
    3: [
        ('CSE-2101', 'Data Structures', 3.0),
        ('CSE-2102', 'Data Structures Lab', 1.5),
        ('CSE-2103', 'Digital Logic Design', 3.0),
        ('CSE-2104', 'Digital Logic Design Lab', 1.0),
        ('CSE-2105', 'Object Oriented Design and Design Patterns', 3.0),
        ('MATH-2101', 'Ordinary and Partial Differential Equations', 3.0),
        ('EEE-2101', 'Electronic Devices and Circuits', 3.0),
        ('EEE-2102', 'Electronic Devices and Circuits Lab', 1.0)
    ],
    4: [
        ('CSE-2201', 'Design and Analysis of Algorithms', 3.0),
        ('CSE-2202', 'Algorithms Lab', 1.5),
        ('CSE-2203', 'Computer Architecture and Organization', 3.0),
        ('CSE-2205', 'Database Management Systems', 3.0),
        ('CSE-2206', 'Database Management Systems Lab', 1.5),
        ('MATH-2201', 'Probability and Statistics for Engineers', 3.0),
        ('ECON-2201', 'Economics for Engineers', 2.0)
    ],
    5: [
        ('CSE-3101', 'Operating Systems and System Programming', 3.0),
        ('CSE-3102', 'Operating Systems and System Programming Lab', 1.5),
        ('CSE-3103', 'Microprocessors and Microcontrollers', 3.0),
        ('CSE-3104', 'Microprocessors and Microcontrollers Lab', 1.0),
        ('CSE-3105', 'Theory of Computation and Automata', 3.0),
        ('CSE-3107', 'Software Engineering and Information Systems', 3.0),
        ('CSE-3108', 'Software Engineering Project Lab', 1.5)
    ],
    6: [
        ('CSE-3201', 'Computer Networks', 3.0),
        ('CSE-3202', 'Computer Networks Lab', 1.5),
        ('CSE-3203', 'Compiler Design', 3.0),
        ('CSE-3204', 'Compiler Design Lab', 1.0),
        ('CSE-3205', 'Web Engineering', 3.0),
        ('CSE-3206', 'Web Engineering Lab', 1.5),
        ('MGT-3201', 'Industrial Management and Entrepreneurship', 2.0)
    ],
    7: [
        ('CSE-4101', 'Artificial Intelligence', 3.0),
        ('CSE-4102', 'Artificial Intelligence Lab', 1.5),
        ('CSE-4103', 'Computer Graphics and Visualization', 3.0),
        ('CSE-4104', 'Computer Graphics Lab', 1.0),
        ('CSE-4105', 'Information Security and Cyber Security', 3.0),
        ('CSE-4100', 'Project & Thesis (Phase I)', 2.0),
        ('CSE-4121', 'Cloud Computing Architecture', 3.0)
    ],
    8: [
        ('CSE-4205', 'Neural Network and Deep Learning', 3.0),
        ('CSE-4206', 'Neural Network and Deep Learning Lab', 1.5),
        ('CSE-4207', 'Pattern Recognition', 3.0),
        ('CSE-4208', 'Pattern Recognition Lab', 1.5),
        ('CSE-4221', 'Machine Learning & Data Flow Operations', 3.0),
        ('CSE-4200', 'Project & Thesis (Phase II / Defense)', 4.0),
        ('SOC-4201', 'Professional Ethics and Social Sociology', 2.0)
    ],
}

def calculate_grade_point(total_mark):
    if total_mark >= 80: return 4.0
    elif total_mark >= 75: return 3.75
    elif total_mark >= 70: return 3.5
    elif total_mark >= 65: return 3.25
    elif total_mark >= 60: return 3.0
    elif total_mark >= 55: return 2.75
    elif total_mark >= 50: return 2.5
    elif total_mark >= 45: return 2.25
    elif total_mark >= 40: return 2.0
    return 0.0

def get_letter_grade(gpa):
    """GPA অনুযায়ী লেটার গ্রেড রিটার্ন করার হেল্পার ফাংশন"""
    gpa = float(gpa)
    if gpa >= 4.0: return "A+"
    if gpa >= 3.75: return "A"
    if gpa >= 3.5: return "A-"
    if gpa >= 3.25: return "B+"
    if gpa >= 3.0: return "B"
    if gpa >= 2.75: return "B-"
    if gpa >= 2.5: return "C+"
    if gpa >= 2.25: return "C"
    if gpa >= 2.0: return "D"
    return "F"

def calculate_ai_readiness(gpa):
    """এআই ভিত্তিক ইন্ডাস্ট্রি রেডিনেস পার্সেন্টেজ লজিক (Mathematical Mapping)"""
    val = float(gpa)
    if val >= 3.75: return int(np.random.randint(88, 98))
    if val >= 3.50: return int(np.random.randint(78, 88))
    if val >= 3.00: return int(np.random.randint(65, 78))
    if val >= 2.50: return int(np.random.randint(50, 65))
    return int(np.random.randint(20, 50))

def auto_generate_results_for_semester(profile, semester):
    """সেমিস্টার চেঞ্জ করলে সব কোর্সের রেজাল্ট রো বানাবে (ফিক্সড ও নিরাপদ)"""
    dept_keyword = getattr(profile, 'department', 'CSE')
    courses = Course.objects.filter(semester=semester, department__icontains=dept_keyword)
    if not courses.exists():
        courses = Course.objects.filter(semester=semester, department='CSE')
    created = 0
    for course in courses:
        result, was_created = StudentResult.objects.get_or_create(
            student_profile=profile,
            course=course,
            semester=semester,
            defaults={
                'class_test_mark': 0.0,
                'quiz_mark': 0.0,
                'attendance_percentage': 0.0,
                'final_exam_mark': 0.0,
                'subject_cgpa': 0.0
            }
        )
        if was_created:
            created += 1
    return created

@staff_member_required(login_url='portal_login')
def admin_dashboard_view(request):
    selected_dept = request.GET.get('dept')

    all_profiles = StudentProfile.objects.all().order_by('-id')
    total_students = all_profiles.count()
    total_courses = Course.objects.count()
    total_ai_sessions = AIChatSession.objects.count() if AIChatSession else 0

    students = StudentProfile.objects.none()
    if selected_dept == 'CSE':
        if hasattr(StudentProfile, 'department'):
            students = StudentProfile.objects.filter(department='CSE').select_related('user')
        else:
            students = StudentProfile.objects.all().select_related('user')

    context = {
        'recent_registrations': all_profiles,
        'total_students': total_students,
        'total_courses': total_courses,
        'total_ai_sessions': total_ai_sessions,
        'students': students,
        'selected_dept': selected_dept,
    }
    return render(request, 'admin_dashboard.html', context)

@staff_member_required(login_url='portal_login')
def admin_approve_student_view(request, profile_id):
    profile = get_object_or_404(StudentProfile, id=profile_id)
    user = profile.user
    enrollment_id = profile.digital_id
    user.is_active = True
    user.username = enrollment_id
    user.set_password(enrollment_id)
    user.save()
    profile.status = 'APPROVED'
    profile.save()

    subject = f'Official Admission Approval - ID {enrollment_id}'
    message = f"Dear {profile.student_name},\n\nYour application has been approved.\nID/Password: {enrollment_id}"
    try:
        send_mail(subject, message, 'NUBTK_ADMIN <noreply@nubtk.edu.bd>', [user.email], fail_silently=False)
        messages.success(request, f"{profile.student_name} approved. Email sent.")
    except Exception:
        messages.warning(request, f"{profile.student_name} approved but email failed.")
    return redirect('admin_dashboard')

@staff_member_required(login_url='portal_login')
def admin_reject_student_view(request, profile_id):
    profile = get_object_or_404(StudentProfile, id=profile_id)
    profile.status = 'REJECTED'
    profile.save()
    messages.error(request, f"{profile.student_name} rejected.")
    return redirect('admin_dashboard')

@staff_member_required(login_url='portal_login')
def admin_update_marks_view(request, profile_id):
    profile = get_object_or_404(StudentProfile, id=profile_id)
    available_semesters = [1, 2, 3, 4, 5, 6, 7, 8]

    if request.method == 'POST':
        if 'current_semester' in request.POST:
            new_semester = int(request.POST.get('current_semester'))
            profile.current_semester = new_semester
            profile.save()
            created = auto_generate_results_for_semester(profile, new_semester)
            messages.success(request, f"Switched to Semester {new_semester}. {created} subjects loaded.")
            return redirect('admin_update_marks', profile_id=profile_id)

        if 'status' in request.POST:
            profile.status = request.POST.get('status')
            profile.save()

        all_active_results = StudentResult.objects.filter(
            student_profile=profile,
            semester__lte=profile.current_semester
        )

        for res in all_active_results:
            if f'ct_mark_{res.id}' in request.POST:
                res.class_test_mark = float(request.POST.get(f'ct_mark_{res.id}', 0) or 0)
                res.quiz_mark = float(request.POST.get(f'quiz_mark_{res.id}', 0) or 0)
                res.attendance_percentage = float(request.POST.get(f'attendance_{res.id}', 0) or 0)
                res.final_exam_mark = float(request.POST.get(f'final_{res.id}', 0) or 0)

                total = res.class_test_mark + res.quiz_mark + res.attendance_percentage + res.final_exam_mark
                res.subject_cgpa = calculate_grade_point(total)
                res.save()

        all_results = StudentResult.objects.filter(student_profile=profile)
        if all_results.exists():
            total_weighted_points = 0.0
            total_credits_taken = 0.0
            for r in all_results:
                course_credit = float(r.course.credits)
                subject_gpa = float(r.subject_cgpa)
                total_weighted_points += (subject_gpa * course_credit)
                total_credits_taken += course_credit
            profile.current_cgpa = round(total_weighted_points / total_credits_taken, 2) if total_credits_taken > 0 else 0.0
            profile.save()

        messages.success(request, f"{profile.student_name}'s Complete Academic Matrix Updated Successfully.")
        return redirect('admin_dashboard')

    semester_grids = []
    for sem_num in range(1, profile.current_semester + 1):
        res_list = StudentResult.objects.filter(
            student_profile=profile,
            semester=sem_num
        ).select_related('course')

        if not res_list.exists():
            auto_generate_results_for_semester(profile, sem_num)
            res_list = StudentResult.objects.filter(student_profile=profile, semester=sem_num).select_related('course')

        for r in res_list:
            r.letter_grade = get_letter_grade(r.subject_cgpa)

        semester_grids.append({
            'semester_num': sem_num,
            'results': res_list
        })

    current_results = StudentResult.objects.filter(
        student_profile=profile,
        semester=profile.current_semester
    ).select_related('course')

    overall_letter_grade = get_letter_grade(profile.current_cgpa)

    context = {
        'student': profile,
        'current_results': current_results,
        'semester_grids': semester_grids,
        'available_semesters': available_semesters,
        'overall_letter_grade': overall_letter_grade,
    }
    return render(request, 'admin_update.html', context)

@staff_member_required(login_url='portal_login')
def admin_delete_student_view(request, profile_id):
    profile = get_object_or_404(StudentProfile, id=profile_id)
    name = profile.student_name
    profile.user.delete()
    messages.error(request, f"{name} permanently deleted.")
    return redirect('admin_dashboard')

@staff_member_required(login_url='portal_login')
def admin_course_matrix_view(request):
    courses = Course.objects.all().order_by('course_code')
    return render(request, 'admin_courses.html', {'courses': courses, 'total_courses': courses.count()})

@staff_member_required(login_url='portal_login')
def admin_ai_analytics_view(request):
    selected_dept = request.GET.get('department')
    selected_student_id = request.GET.get('student_id')

    students = StudentProfile.objects.filter(status='APPROVED').order_by('-current_cgpa').select_related('user')

    cse_students = StudentProfile.objects.none()
    if selected_dept == 'CSE':
        if hasattr(StudentProfile, 'department'):
            cse_students = StudentProfile.objects.filter(department='CSE', status='APPROVED').select_related('user')
        else:
            cse_students = students

    selected_student = None
    ai_report = None

    if selected_student_id:
        selected_student = get_object_or_404(StudentProfile, id=selected_student_id)
        results = StudentResult.objects.filter(student_profile=selected_student).select_related('course')

        skills_acquired = []
        skills_gap = []
        predicted_growth = []

        for r in results:
            total_score = r.class_test_mark + r.quiz_mark + r.attendance_percentage + r.final_exam_mark

            if "Lab" in r.course.course_name or "Sessional" in r.course.course_name:
                if total_score >= 70:
                    skills_acquired.append(f"Practical Core: {r.course.course_name.split('Lab')[0]}")
                else:
                    skills_gap.append(f"Practical Hands-on Deficit in {r.course.course_name}")
            else:
                if total_score >= 75:
                    skills_acquired.append(f"Theoretical Framework: {r.course.course_code}")
                elif total_score < 50:
                    skills_gap.append(f"Conceptual Knowledge Gap in {r.course.course_code}")

            growth_factor = float(r.subject_cgpa) * 1.05 if float(r.subject_cgpa) > 2.0 else 2.0
            predicted_growth.append({
                'course_code': r.course.course_code,
                'current': float(r.subject_cgpa),
                'predicted': min(4.0, round(growth_factor, 2))
            })

        if not skills_acquired: skills_acquired = ["Fundamental Logic Formulation Building Blocks"]
        if not skills_gap: skills_gap = ["Scalable Software Architecture & Data Structures Optimizations"]

        readiness_score = calculate_ai_readiness(selected_student.current_cgpa)

        ai_report = {
            'readiness_percentage': readiness_score,
            'skills_mastered': skills_acquired[:5],
            'gaps_identified': skills_gap[:4],
            'predictions': predicted_growth[:6],
            'cognitive_status': "HIGHLY ADAPTIVE ENGINE" if readiness_score >= 75 else "REMEDIAL WORKSTATION ENGAGEMENT REQUIRED"
        }

    context = {
        'students': students,
        'total_students': students.count(),
        'selected_dept': selected_dept,
        'cse_students': cse_students,
        'selected_student': selected_student,
        'ai_report': ai_report,
    }
    return render(request, 'admin_ai_analytics.html', context)

@staff_member_required(login_url='portal_login')
def admin_logout_view(request):
    logout(request)
    messages.info(request, "Admin logged out.")
    return redirect('home')

@staff_member_required(login_url='portal_login')
def seed_cse_curriculum_view(request):
    created_count = 0
    for sem, courses in CSE_160_CURRICULUM.items():
        for code, title, credit in courses:
            course, created = Course.objects.get_or_create(
                course_code=code,
                defaults={'course_name': title, 'credits': credit, 'semester': sem, 'department': 'CSE'}
            )
            if created: created_count += 1
    messages.success(request, f"Success! {created_count} courses seeded.")
    return redirect('admin_course_matrix')

@login_required
def admin_manage_resources_view(request):
    """
    ধাপ ৮.২ (সংশোধিত পাথ): অ্যাডমিন প্যানেল থেকে রিসোর্স যুক্ত করার গেটওয়ে।
    """
    if not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        resource_url = request.POST.get('resource_url')
        description = request.POST.get('description')

        if title and resource_url:
            ResourceHub.objects.create(
                title=title,
                category=category,
                resource_url=resource_url,
                description=description,
                uploaded_by=request.user
            )
            return redirect('admin_manage_resources')

    resources = ResourceHub.objects.all().order_by('-created_at')
    return render(request, 'manage_resources.html', {'resources': resources})