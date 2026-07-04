from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from apps.academics.models import StudentProfile, ResourceHub, PaymentHistory, StudentPracticalLog, StudentResult
from apps.ai_ml_engine.analyzer import calculate_global_eligibility
from apps.ai_ml_engine.models_ml import train_and_predict_career_path
from apps.ai_ml_engine.neural_net import predict_future_cgpa_with_nn

@login_required
def student_dashboard_view(request):
    if not getattr(request.user, 'is_student', False):
        return redirect('home')

    try:
        profile = StudentProfile.objects.select_related('user').prefetch_related('payments').get(user=request.user)

        ai_metrics = calculate_global_eligibility(profile)
        ml_predictions = train_and_predict_career_path(profile)
        nn_outputs = predict_future_cgpa_with_nn(profile)

        payments = profile.payments.all().order_by('semester', 'due_date')
        total_payable = sum([p.amount for p in payments])
        total_paid = sum([p.amount for p in payments if p.status == 'PAID'])

        context = {
            'profile': profile,
            'eligibility_score': ai_metrics['eligibility_percentage'],
            'vector_data': ai_metrics['student_vector'],
            'career_track': ml_predictions['predicted_track'],
            'ml_confidence': ml_predictions['confidence'],
            'ml_algo': ml_predictions['algorithm_used'],
            'predicted_cgpa': nn_outputs['predicted_future_cgpa'],
            'nn_status': nn_outputs['status'],
            'payments': payments,
            'total_payable': total_payable,
            'total_paid': total_paid,
            'due_amount': total_payable - total_paid,
        }

    except Exception as e:
        print(f"Safety Shield Triggered: {e}")
        profile = get_object_or_404(StudentProfile, user=request.user)
        payments = profile.payments.all().order_by('semester', 'due_date')
        total_payable = sum([p.amount for p in payments])
        total_paid = sum([p.amount for p in payments if p.status == 'PAID'])

        context = {
            'profile': profile,
            'eligibility_score': 0.0,
            'vector_data': [],
            'career_track': "Under Analysis",
            'ml_confidence': 0,
            'ml_algo': "Safe Mode",
            'predicted_cgpa': profile.current_cgpa,
            'nn_status': "Safety Shield Active",
            'payments': payments,
            'total_payable': total_payable,
            'total_paid': total_paid,
            'due_amount': total_payable - total_paid,
        }

    return render(request, 'student.html', context)

@login_required
def student_resource_hub_view(request):
    if not getattr(request.user, 'is_student', False):
        return redirect('home')
    resources = ResourceHub.objects.all().order_by('category')
    return render(request, 'dashboard/resource_hub.html', {'resources': resources})

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
def process_student_payment_gate(request, payment_id):
    if not getattr(request.user, 'is_student', False):
        return redirect('home')
    payment = get_object_or_404(PaymentHistory, id=payment_id, student_profile__user=request.user)
    if payment.status == 'PENDING':
        payment.status = 'PAID'
        payment.save()
        messages.success(request, f"Payment successful! {payment.title} marked as PAID.")
    return redirect('student_dashboard')

@login_required
def student_practical_skills_view(request):
    """
    লেয়ার ২.১: স্টুডেন্টের প্র্যাকটিক্যাল লগের ওপর ভিত্তি করে
    এআই রেডার ম্যাট্রিক্স ও রিমাইন্ডার জেনারেশন ইঞ্জিন।
    """
    if not getattr(request.user, 'is_student', False):
        return redirect('home')

    profile = get_object_or_404(StudentProfile, user=request.user)

    # [লেয়ার ১.২] ফর্ম সাবমিশন হ্যান্ডলার (আগের মতোই থাকবে)
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

    # ডাটাবেজ থেকে স্টুডেন্টের সব সাবজেক্ট ও অলরেডি সাবমিট করা লগ তুলে আনা
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

    # --- এআই রেডার ম্যাট্রিক্স লজিক (কি-ওয়ার্ড স্ক্যানিং ও গ্যাপ ডিটেকশন) ---
    coding_score = 10
    soft_skills_score = 10
    total_logs_count = all_logs.count()

    # যদি স্টুডেন্ট লগ সাবমিট করা শুরু করে, তবে তার ইনপুট স্ক্যান করে প্রগ্রেস বাড়ানো
    for log in all_logs:
        full_text = f"{log.tools_learned or ''} {log.project_outcome or ''} {log.skill_gaps_declared or ''}".lower()

        # কোডিং ও টুলস ট্র্যাকিং
        if any(w in full_text for w in ['git', 'github', 'python', 'java', 'c++', 'code', 'vs code', 'linux']):
            coding_score += 20
        # সফট স্কিলস ও প্রেজেন্টেশন ট্র্যাকিং
        if any(w in full_text for w in ['english', 'presentation', 'slide', 'powerpoint', 'communication', 'ভয় পাই', 'ভয়']):
            soft_skills_score += 20

    # ক্যাপ লিমিট ১০০% এ লক করা
    coding_score = min(coding_score, 100)
    soft_skills_score = min(soft_skills_score, 100)

    # --- এআই ডাইনামিক রিমাইন্ডার জেনারেটর ---
    ai_reminders = []
    first_name = profile.student_name.split()[0] if profile.student_name else "তুমি"

    if total_logs_count == 0:
        ai_reminders.append({
            'type': 'danger',
            'icon': 'fa-exclamation-triangle',
            'message': f"{first_name}, তোমার প্র্যাকটিক্যাল স্কিল ম্যাট্রিক্স একদম শূন্য! চাকরির বাজার অনেক কঠিন। দ্রুত যেকোনো একটি সাবজেক্টের 'Log Practical' বাটনে ক্লিক করে তোমার প্রোগ্রেস আপডেট করো।"
        })
    else:
        if coding_score < 50:
            ai_reminders.append({
                'type': 'warning',
                'icon': 'fa-code',
                'message': f"তোমার কোর কোডিং রেডিডনেস মাত্র {coding_score}%! থার্ড ইয়ারের স্টুডেন্ট হিসেবে তোমার গিটহাব প্রোফাইল ও লিনাক্স কমান্ডে ঘাটতি আছে। কোডিং ল্যাবে আরও মনোযোগ দাও।"
            })
        if soft_skills_score < 50:
            ai_reminders.append({
                'type': 'info',
                'icon': 'fa-comments',
                'message': f"ইংরেজি এবং প্রেজেন্টেশন স্কিল গ্যাপ ধরা পড়েছে ({soft_skills_score}%)! ভাইভা ও ডিফেন্সে ভালো করতে এখনই স্লাইড মেকিং এবং ইংরেজিতে কথা বলার জড়তা দূর করো।"
            })
        if coding_score >= 60 and soft_skills_score >= 60:
            ai_reminders.append({
                'type': 'success',
                'icon': 'fa-check-double',
                'message': "দারুণ অগ্রগতি! তোমার টেকনিক্যাল ও সফট স্কিল ব্যালেন্সড অবস্থায় আছে। এবার একটি প্রফেশনাল সিভি (CV) তৈরি করে লিঙ্কডইনে চাকরির খোঁজ শুরু করতে পারো।"
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