import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from apps.academics.models import StudentProfile
from apps.ai_ml_engine.bot_engine import ask_hybrid_copilot_brain
from apps.ai_ml_engine.models import AIChatSession
from .student_views import calculate_real_academic_metrics


@login_required
def student_ai_chat_hub_view(request):
    if not getattr(request.user, 'is_student', False):
        return redirect('home')

    try:
        profile = request.user.student_profile
    except AttributeError:
        profile = get_object_or_404(StudentProfile, user=request.user)

    # ডাটাবেজ থেকে রিয়েল-টাইম মার্কস ও প্র্যাকটিক্যাল মেট্রিক্স পাওয়া
    metrics = calculate_real_academic_metrics(profile)

    if request.method == 'POST':
        user_message = request.POST.get('user_message', '').strip()
        image_file = request.FILES.get('attached_image')

        image_base64 = None
        if image_file:
            try:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            except Exception:
                image_base64 = None

        if user_message or image_base64:
            ai_reply = ask_hybrid_copilot_brain(
                student_profile=profile,
                user_message=user_message,
                image_data_base64=image_base64,
                context_data=metrics
            )

            # আপনার ডাটাবেজ মডেলে তৈরি ফিল্ড অনুযায়ী সেভ
            AIChatSession.objects.create(
                student=profile,
                user_message=user_message if user_message else "[Uploaded Image]",
                ai_response=ai_reply
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'user_message': user_message if user_message else "[Image Review Request]",
                    'ai_response': ai_reply
                })

            return redirect('student_ai_chat_hub')

    # আপনার মডেলে timestamp ফিল্ড রয়েছে
    conversations = AIChatSession.objects.filter(student=profile).order_by('timestamp')

    context = {
        'profile': profile,
        'eligibility_score': metrics['eligibility_score'],
        'career_track': metrics['career_track'],
        'predicted_cgpa': metrics['predicted_cgpa'],
        'conversations': conversations
    }
    return render(request, 'dashboard/ai_chat_hub.html', context)