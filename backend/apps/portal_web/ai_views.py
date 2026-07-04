import base64
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.academics.models import StudentProfile
from apps.ai_ml_engine.bot_engine import ask_hybrid_copilot_brain
from apps.ai_ml_engine.models import AIChatSession

@login_required
def student_ai_chat_hub_view(request):
    if not getattr(request.user, 'is_student', False):
        return redirect('home')

    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('home')

    eligibility_score = 75
    career_track = "Data Science & Machine Learning"
    predicted_cgpa = "3.64"

    context_data = {
        'eligibility_score': eligibility_score,
        'career_track': career_track,
        'predicted_cgpa': predicted_cgpa
    }

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
            ai_reply = ask_hybrid_copilot_brain(profile, user_message, image_base64, context_data)

            # তোমার মডেলে sender_type নেই, তাই বাদ দিলাম
            AIChatSession.objects.create(
                student=profile,
                user_message=user_message if user_message else "[Uploaded Image]",
                ai_response=ai_reply
            )

            # AJAX রিকোয়েস্ট হলে JSON দাও, নরমাল হলে রিডাইরেক্ট
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'user_message': user_message,
                    'ai_response': ai_reply
                })

            return redirect('student_ai_chat_hub')

    # তোমার মডেলে timestamp আছে, created_at নেই
    conversations = AIChatSession.objects.filter(student=profile).order_by('timestamp')

    context = {
        'profile': profile,
        'eligibility_score': eligibility_score,
        'career_track': career_track,
        'predicted_cgpa': predicted_cgpa,
        'conversations': conversations
    }
    return render(request, 'dashboard/ai_chat_hub.html', context)