<<<<<<< HEAD
import os
import requests
import json
from django.conf import settings
from apps.academics.models import StudentPracticalLog

def detect_task_category(user_message, has_image=False):
    msg_lower = user_message.lower() if user_message else ""

    if has_image:
        return "VISION"

    coding_keywords = ['code', 'python', 'django', 'html', 'css', 'javascript', 'bug', 'error', 'function', 'class', 'database', 'sql']
    if any(keyword in msg_lower for keyword in coding_keywords):
        return "CODING"

    math_keywords = ['math', 'solve', 'calculate', 'prove', 'equation', 'algorithm', 'gpa', 'cgpa', 'result', 'mark']
    if any(keyword in msg_lower for keyword in math_keywords):
        return "REASONING"

    return "GENERAL"


def ask_hybrid_copilot_brain(student_profile, user_message, image_data_base64=None, context_data=None):
    openrouter_key = getattr(settings, 'OPENROUTER_API_KEY', '') or os.environ.get("OPENROUTER_API_KEY", "")

    if not openrouter_key:
        print("[OpenRouter Error] OPENROUTER_API_KEY settings বা .env ফাইলে পাওয়া যায়নি!")
        return "System Configuration Warning: .env ফাইলে OPENROUTER_API_KEY পাওয়া যায়নি।"

    student_gaps_context = ""
    try:
        practical_logs = StudentPracticalLog.objects.filter(student_profile=student_profile)
        for log in practical_logs:
            student_gaps_context += f"- Course {log.subject_code} ({log.subject_name}): Tools: [{log.tools_learned}], Gaps: [{log.skill_gaps_declared}]\n"
    except Exception as e:
        student_gaps_context = "No logs available."

    eligibility = context_data.get('eligibility_score', 0) if context_data else 0
    career_track = context_data.get('career_track', 'Software Engineering') if context_data else 'Software Engineering'
    predicted_cgpa = context_data.get('predicted_cgpa', '0.00') if context_data else '0.00'

    student_name = getattr(student_profile, 'student_name', 'Student')
    current_semester = getattr(student_profile, 'current_semester', '1st')

    system_instruction = (
        f"You are 'NUBTK Copilot AI Workspace', the smart interactive student proctor at Northern University Bangladesh Trust Khulna.\n"
        f"Student Name: '{student_name}' | Current Semester: {current_semester}.\n\n"
        f"--- LIVE ACADEMIC CORE MEMORY (STRICT TRUTH) ---\n"
        f"- Current Overall Skill Score: {eligibility}%\n"
        f"- Recommended Career Track: {career_track}\n"
        f"- Current Semester CGPA Forecast: {predicted_cgpa}\n"
        f"\n--- STUDENT PRACTICAL LOGS & WEAKNESSES ---\n"
        f"{student_gaps_context if student_gaps_context else 'No practical logs submitted yet.'}\n"
        f"-----------------------------------------\n\n"
        f"CRITICAL RULE: Always use the exact values provided in the LIVE ACADEMIC CORE MEMORY above (Skill Score: {eligibility}%, Track: {career_track}, CGPA: {predicted_cgpa}). NEVER make up old figures like 75%.\n"
        f"Guidance Style: Friendly, professional academic mentor in natural Bengali/Banglish. Analyze student results, suggest skill improvements, and answer directly."
    )

    has_image = bool(image_data_base64)
    task_category = detect_task_category(user_message, has_image)

    # ওপেনরাউটারের ভ্যালিড ফ্রি আইডি ও অটো রাউটিং ক্লাস্টার
    fallback_models = {
        "GENERAL": [
            "google/gemini-2.0-flash-exp:free",
            "openrouter/auto",
            "meta-llama/llama-3.2-11b-vision-instruct:free",
            "qwen/qwen-2.5-coder-32b-instruct:free"
        ],
        "CODING": [
            "qwen/qwen-2.5-coder-32b-instruct:free",
            "google/gemini-2.0-flash-exp:free",
            "openrouter/auto"
        ],
        "REASONING": [
            "google/gemini-2.0-flash-exp:free",
            "openrouter/auto"
        ],
        "VISION": [
            "google/gemini-2.0-flash-exp:free",
            "meta-llama/llama-3.2-11b-vision-instruct:free"
        ]
    }

    models_to_execute = fallback_models.get(task_category, ["google/gemini-2.0-flash-exp:free", "openrouter/auto"])

    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://127.0.0.1:8000",
        "X-Title": "NUBTK Copilot ERP"
    }

    text_message = user_message if user_message else "Hello"
    if image_data_base64 and task_category == "VISION":
        messages_content = [
            {"type": "text", "text": text_message},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_data_base64}"}
            }
        ]
    else:
        messages_content = text_message

    for model in models_to_execute:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": messages_content}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        try:
            print(f"[OpenRouter Attempting Model]: {model}")
            response = requests.post(openrouter_url, headers=headers, data=json.dumps(payload), timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    ai_text = result['choices'][0]['message']['content']
                    print(f"[OpenRouter Success]: Response received from {model}")
                    return ai_text
            else:
                print(f"[OpenRouter API Error] Model: {model} | Status: {response.status_code} | Body: {response.text}")

        except Exception as err:
            print(f"[OpenRouter Exception] Model: {model} | Error: {str(err)}")
            continue

=======
import os
import requests
import json
from django.conf import settings
from apps.academics.models import StudentPracticalLog

def detect_task_category(user_message, has_image=False):
    msg_lower = user_message.lower() if user_message else ""

    if has_image:
        return "VISION"

    coding_keywords = ['code', 'python', 'django', 'html', 'css', 'javascript', 'bug', 'error', 'function', 'class', 'database', 'sql']
    if any(keyword in msg_lower for keyword in coding_keywords):
        return "CODING"

    math_keywords = ['math', 'solve', 'calculate', 'prove', 'equation', 'algorithm', 'gpa', 'cgpa', 'result', 'mark']
    if any(keyword in msg_lower for keyword in math_keywords):
        return "REASONING"

    return "GENERAL"


def ask_hybrid_copilot_brain(student_profile, user_message, image_data_base64=None, context_data=None):
    openrouter_key = getattr(settings, 'OPENROUTER_API_KEY', '') or os.environ.get("OPENROUTER_API_KEY", "")

    if not openrouter_key:
        print("[OpenRouter Error] OPENROUTER_API_KEY settings বা .env ফাইলে পাওয়া যায়নি!")
        return "System Configuration Warning: .env ফাইলে OPENROUTER_API_KEY পাওয়া যায়নি।"

    student_gaps_context = ""
    try:
        practical_logs = StudentPracticalLog.objects.filter(student_profile=student_profile)
        for log in practical_logs:
            student_gaps_context += f"- Course {log.subject_code} ({log.subject_name}): Tools: [{log.tools_learned}], Gaps: [{log.skill_gaps_declared}]\n"
    except Exception as e:
        student_gaps_context = "No logs available."

    eligibility = context_data.get('eligibility_score', 0) if context_data else 0
    career_track = context_data.get('career_track', 'Software Engineering') if context_data else 'Software Engineering'
    predicted_cgpa = context_data.get('predicted_cgpa', '0.00') if context_data else '0.00'

    student_name = getattr(student_profile, 'student_name', 'Student')
    current_semester = getattr(student_profile, 'current_semester', '1st')

    system_instruction = (
        f"You are 'NUBTK Copilot AI Workspace', the smart interactive student proctor at Northern University Bangladesh Trust Khulna.\n"
        f"Student Name: '{student_name}' | Current Semester: {current_semester}.\n\n"
        f"--- LIVE ACADEMIC CORE MEMORY (STRICT TRUTH) ---\n"
        f"- Current Overall Skill Score: {eligibility}%\n"
        f"- Recommended Career Track: {career_track}\n"
        f"- Current Semester CGPA Forecast: {predicted_cgpa}\n"
        f"\n--- STUDENT PRACTICAL LOGS & WEAKNESSES ---\n"
        f"{student_gaps_context if student_gaps_context else 'No practical logs submitted yet.'}\n"
        f"-----------------------------------------\n\n"
        f"CRITICAL RULE: Always use the exact values provided in the LIVE ACADEMIC CORE MEMORY above (Skill Score: {eligibility}%, Track: {career_track}, CGPA: {predicted_cgpa}). NEVER make up old figures like 75%.\n"
        f"Guidance Style: Friendly, professional academic mentor in natural Bengali/Banglish. Analyze student results, suggest skill improvements, and answer directly."
    )

    has_image = bool(image_data_base64)
    task_category = detect_task_category(user_message, has_image)

    # ওপেনরাউটারের ভ্যালিড ফ্রি আইডি ও অটো রাউটিং ক্লাস্টার
    fallback_models = {
        "GENERAL": [
            "google/gemini-2.0-flash-exp:free",
            "openrouter/auto",
            "meta-llama/llama-3.2-11b-vision-instruct:free",
            "qwen/qwen-2.5-coder-32b-instruct:free"
        ],
        "CODING": [
            "qwen/qwen-2.5-coder-32b-instruct:free",
            "google/gemini-2.0-flash-exp:free",
            "openrouter/auto"
        ],
        "REASONING": [
            "google/gemini-2.0-flash-exp:free",
            "openrouter/auto"
        ],
        "VISION": [
            "google/gemini-2.0-flash-exp:free",
            "meta-llama/llama-3.2-11b-vision-instruct:free"
        ]
    }

    models_to_execute = fallback_models.get(task_category, ["google/gemini-2.0-flash-exp:free", "openrouter/auto"])

    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://127.0.0.1:8000",
        "X-Title": "NUBTK Copilot ERP"
    }

    text_message = user_message if user_message else "Hello"
    if image_data_base64 and task_category == "VISION":
        messages_content = [
            {"type": "text", "text": text_message},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_data_base64}"}
            }
        ]
    else:
        messages_content = text_message

    for model in models_to_execute:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": messages_content}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        try:
            print(f"[OpenRouter Attempting Model]: {model}")
            response = requests.post(openrouter_url, headers=headers, data=json.dumps(payload), timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    ai_text = result['choices'][0]['message']['content']
                    print(f"[OpenRouter Success]: Response received from {model}")
                    return ai_text
            else:
                print(f"[OpenRouter API Error] Model: {model} | Status: {response.status_code} | Body: {response.text}")

        except Exception as err:
            print(f"[OpenRouter Exception] Model: {model} | Error: {str(err)}")
            continue

>>>>>>> cc3d22ff42f8869ce0a4aa7e99e905cb0f74f89f
    return "ওপেনরাউটার ফ্রি সার্ভারে কানেক্ট করতে সাময়িক সমস্যা হচ্ছে। অনুগ্রহ করে ২-৩ সেকেন্ড পর আবার চেষ্টা করুন।"