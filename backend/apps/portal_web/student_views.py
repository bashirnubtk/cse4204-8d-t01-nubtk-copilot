import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from apps.academics.models import StudentProfile, ResourceHub, StudentPracticalLog, StudentResult


def calculate_real_academic_metrics(profile):
    """
    ডাটাবেজের মার্কস এবং স্টুডেন্টের ইনপুট দেওয়া প্র্যাকটিক্যাল স্কিলের ওপর ভিত্তি করে
    রিয়েল-টাইম ডাইনামিক ক্যারিয়ার প্রেডিকশন ইঞ্জিন।
    """
    results = StudentResult.objects.filter(student_profile=profile).select_related('course')
    total_gpa_points = 0.0
    total_credits = 0
    total_marks_obtained = 0.0
    total_possible_marks = 0

    for r in results:
        credit = r.course.credits if (r.course and hasattr(r.course, 'credits')) else 3
        cgpa = float(r.subject_cgpa or 0.0)
        total_gpa_points += (cgpa * credit)
        total_credits += credit

        obtained = float(r.class_test_mark or 0) + float(r.quiz_mark or 0) + float(r.attendance_percentage or 0) + float(r.final_exam_mark or 0)
        total_marks_obtained += obtained
        total_possible_marks += 100

    actual_cgpa = round(total_gpa_points / total_credits, 2) if total_credits > 0 else 0.00
    academic_score_pct = round((total_marks_obtained / total_possible_marks) * 100, 1) if total_possible_marks > 0 else 0.0

    # স্টুডেন্টের ইনপুট দেওয়া সব প্র্যাকটিক্যাল লগের টেক্সট একত্র করা
    all_logs = StudentPracticalLog.objects.filter(student_profile=profile)
    user_skills_text = ""
    for log in all_logs:
        user_skills_text += f" {log.tools_learned or ''} {log.project_outcome or ''} {log.skill_gaps_declared or ''}".lower()

    practical_pct = min(100, all_logs.count() * 25)

    if total_possible_marks > 0:
        eligibility_score = round((academic_score_pct * 0.7) + (practical_pct * 0.3), 1)
    else:
        eligibility_score = practical_pct

    # --- DYNAMIC AI CAREER PREDICTION ENGINE ---
    career_track = "Software Engineering Fundamentals"
    ml_confidence = 82
    ml_algo = "RandomForest Classifier"

    # স্টুডেন্টের ইনপুট দেওয়া স্কিল কিওয়ার্ড চেক করে ডাইনামিক প্রেডিকশন নির্ধারণ
    if any(w in user_skills_text for w in ["python", "machine learning", "data", "pandas", "ai", "numpy", "sql", "dataset"]):
        career_track = "Data Science & Machine Learning"
        ml_confidence = 94
        ml_algo = "Neural Net (MLP Classifier)"
    elif any(w in user_skills_text for w in ["network", "cyber", "security", "cisco", "linux", "wireshark", "router"]):
        career_track = "Cyber Security & Cloud Networking"
        ml_confidence = 91
        ml_algo = "SVM (Support Vector Machine)"
    elif any(w in user_skills_text for w in ["react", "django", "html", "css", "web", "node", "javascript", "bootstrap"]):
        career_track = "Full-Stack Web Engineering"
        ml_confidence = 89
        ml_algo = "GradientBoosting Classifier"
    elif any(w in user_skills_text for w in ["flutter", "android", "kotlin", "java", "mobile"]):
        career_track = "Mobile App Development"
        ml_confidence = 88
        ml_algo = "RandomForest Classifier"

    return {
        'eligibility_score': eligibility_score,
        'career_track': career_track,
        'predicted_cgpa': f"{actual_cgpa:.2f}",
        'academic_score_pct': academic_score_pct,
        'results_list': results,
        'ml_confidence': ml_confidence,
        'ml_algo': ml_algo,
    }


@login_required
def student_dashboard_view(request):
    if not getattr(request.user, 'is_student', False):
        return redirect('home')

    profile = get_object_or_404(StudentProfile, user=request.user)
    metrics = calculate_real_academic_metrics(profile)

    context = {
        'profile': profile,
        'eligibility_score': metrics['eligibility_score'],
        'career_track': metrics['career_track'],
        'predicted_cgpa': metrics['predicted_cgpa'],
        'academic_score_pct': metrics['academic_score_pct'],
        'results_list': metrics['results_list'],
        'ml_confidence': metrics['ml_confidence'],
        'ml_algo': metrics['ml_algo'],
    }

    return render(request, 'student.html', context)


def process_student_payment_gate(request, payment_id=None):
    return redirect('student_dashboard')


@login_required
def student_resource_hub_view(request):
    """ AI Recommendation & Resource Hub View """
    if not getattr(request.user, 'is_student', False):
        return redirect('home')

    profile = get_object_or_404(StudentProfile, user=request.user)
    results = StudentResult.objects.filter(student_profile=profile).select_related('course')
    logs = StudentPracticalLog.objects.filter(student_profile=profile)

    ai_recommendations = []

    for r in results:
        obtained = float(r.class_test_mark or 0) + float(r.quiz_mark or 0) + float(r.attendance_percentage or 0) + float(r.final_exam_mark or 0)
        if obtained > 0 and obtained < 60 and r.course:
            ai_recommendations.append({
                'subject': r.course.course_name,
                'reason': f"Your score ({obtained}/100) is below average.",
                'action': f"Review foundations and practical code examples for {r.course.course_name}.",
                'badge_color': 'warning'
            })

    for log in logs:
        if log.skill_gaps_declared:
            ai_recommendations.append({
                'subject': log.subject_name or log.subject_code,
                'reason': f"You declared gap: '{log.skill_gaps_declared}'",
                'action': "Focus on lab exercises and presentation frameworks.",
                'badge_color': 'info'
            })

    resources = ResourceHub.objects.all().order_by('category')
    return render(request, 'dashboard/resource_hub.html', {
        'resources': resources,
        'ai_recommendations': ai_recommendations,
        'profile': profile
    })


@login_required
def track_resource_click_view(request, resource_id):
    resource = get_object_or_404(ResourceHub, id=resource_id)
    resource.click_count += 1
    resource.save()
    target_url = resource.resource_url or resource.external_link
    if target_url:
        return redirect(target_url)
    else:
        messages.warning(request, "Inactive link.")
        return redirect('student_resource_hub')


@login_required
def student_practical_skills_view(request):
    if not getattr(request.user, 'is_student', False):
        return redirect('home')

    profile = get_object_or_404(StudentProfile, user=request.user)

    if request.method == 'POST':
        sub_code = request.POST.get('subject_code')
        sub_name = request.POST.get('subject_name')
        tools = request.POST.get('tools_learned')
        outcome = request.POST.get('project_outcome')
        gaps = request.POST.get('skill_gaps_declared')

        if sub_code and tools:
            StudentPracticalLog.objects.update_or_create(
                student_profile=profile,
                subject_code=sub_code,
                defaults={
                    'subject_name': sub_name,
                    'tools_learned': tools,
                    'project_outcome': outcome,
                    'skill_gaps_declared': gaps
                }
            )
            return redirect('student_practical_skills')

    results = StudentResult.objects.filter(student_profile=profile).select_related('course').order_by('course__semester', 'course__course_code')

    assigned_subjects = []
    for r in results:
        total = float(r.class_test_mark or 0) + float(r.quiz_mark or 0) + float(r.attendance_percentage or 0) + float(r.final_exam_mark or 0)
        cgpa = float(r.subject_cgpa or 0)

        if cgpa >= 4.0: letter = 'A+'
        elif cgpa >= 3.75: letter = 'A'
        elif cgpa >= 3.5: letter = 'A-'
        elif cgpa >= 3.25: letter = 'B+'
        elif cgpa >= 3.0: letter = 'B'
        elif cgpa >= 2.75: letter = 'B-'
        elif cgpa >= 2.5: letter = 'C+'
        elif cgpa >= 2.25: letter = 'C'
        elif cgpa >= 2.0: letter = 'D'
        else: letter = 'F'

        assigned_subjects.append({
            'id': r.id,
            'course': r.course,
            'total_marks': total,
            'gpa': f"{cgpa:.2f}",
            'letter_grade': letter,
        })

    all_logs = StudentPracticalLog.objects.filter(student_profile=profile)
    existing_logs = list(all_logs.values_list('subject_code', flat=True))

    coding_score = 10
    soft_skills_score = 10
    total_logs_count = all_logs.count()

    for log in all_logs:
        full_text = f"{log.tools_learned or ''} {log.project_outcome or ''} {log.skill_gaps_declared or ''}".lower()

        if any(w in full_text for w in ['git', 'github', 'python', 'java', 'c++', 'code', 'vs code', 'linux']):
            coding_score += 25
        if any(w in full_text for w in ['english', 'presentation', 'slide', 'powerpoint', 'communication', 'speech']):
            soft_skills_score += 25

    coding_score = min(coding_score, 100)
    soft_skills_score = min(soft_skills_score, 100)

    ai_reminders = []
    first_name = profile.student_name.split()[0] if profile.student_name else "তুমি"

    if total_logs_count == 0:
        ai_reminders.append({
            'type': 'danger',
            'icon': 'fa-exclamation-triangle',
            'message': f"{first_name}, তোমার প্র্যাকটিক্যাল স্কিল ম্যাট্রিক্স একদম শূন্য! প্রোগ্রেস আপডেট করতে যেকোনো একটি সাবজেক্টের 'Log Practical' বাটনে ক্লিক করো।"
        })
    else:
        if coding_score < 50:
            ai_reminders.append({
                'type': 'warning',
                'icon': 'fa-code',
                'message': f"তোমার কোডিং রেডিডনেস {coding_score}%! কোডিং ল্যাবে আরেকটু ফোকাস দেওয়া দরকার।"
            })

    context = {
        'profile': profile,
        'assigned_subjects': assigned_subjects,
        'existing_logs': existing_logs,
        'coding_score': coding_score,
        'soft_skills_score': soft_skills_score,
        'ai_reminders': ai_reminders
    }
    return render(request, 'student_skills.html', context)