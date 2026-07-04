import os
import requests
import json
from apps.academics.models import StudentPracticalLog

def detect_task_category(user_message, has_image=False):
    """
    ইউজারের মেসেজ এবং ফাইল টাইপ এনালাইসিস করে কাজের ক্যাটাগরি 
    এবং আপনার চার্ট অনুযায়ী বেস্ট ফ্রি মডেল আইডি সিলেক্ট করার সাব-ইঞ্জিন।
    """
    msg_lower = user_message.lower()
    
    if has_image:
        return "VISION", "nex-agi/nex-n2-pro:free"
        
    # কোডিং রিকোয়ারমেন্টস ডিটেকশন
    coding_keywords = ['code', 'python', 'django', 'html', 'css', 'javascript', 'bug', 'error', 'function', 'class', 'database', 'sql']
    if any(keyword in msg_lower for keyword in coding_keywords):
        return "CODING", "qwen/qwen3-coder:free"
        
    # ম্যাথ বা রিজনিং ডিটেকশন
    math_keywords = ['math', 'solve', 'calculate', 'prove', 'equation', 'algorithm', 'gpa', 'cgpa']
    if any(keyword in msg_lower for keyword in math_keywords):
        return "REASONING", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
        
    # ডিফল্ট জেনারেট চ্যাট
    return "GENERAL", "openai/gpt-oss-20b:free"


def ask_hybrid_copilot_brain(student_profile, user_message, image_data_base64=None, context_data=None):
    """
    ধাপ ৪.১ (অগ্রবর্তী হাইব্রিড সংস্করণ): ওপেনরাউটার ফ্রি মডেল ও গুগল ডিরেক্ট 
    জেমিনির বুদ্ধিমত্তাকে এক সুতোয় বেঁধে তৈরি করা চূড়ান্ত মেন্টর ইঞ্জিন।
    """
    # .env থেকে এপিআই কী-গুলো রিড করা
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    google_key = os.getenv("GEMINI_API_KEY", "")
    
    # ১. ডাটাবেজ থেকে স্টুডেন্টের প্র্যাকটিক্যাল লগ কনটেক্সট প্রিপেয়ার করা (লেয়ার ১)
    practical_logs = StudentPracticalLog.objects.filter(student_profile=student_profile)
    student_gaps_context = ""
    for log in practical_logs:
        student_gaps_context += f"- Course {log.subject_code} ({log.subject_name}): Tools: [{log.tools_learned}], Gaps: [{log.skill_gaps_declared}]\n"

    # ২. মেটাডাটা ভেক্টর ইন্টিগ্রেশন (ড্যাশবোর্ড মেমোরি)
    eligibility = context_data.get('eligibility_score', 0) if context_data else 0
    career_track = context_data.get('career_track', 'Software Engineering') if context_data else 'Software Engineering'
    predicted_cgpa = context_data.get('predicted_cgpa', '0.00') if context_data else '0.00'

    # ৩. কাস্টম সিস্টেম প্রম্পট (হিউম্যানাইজড মেন্টর গাইডলাইন)
    system_instruction = (
        f"You are 'NUBTK Copilot AI Workspace', the smart interactive student proctor at Northern University.\n"
        f"Student Name: '{student_profile.student_name}' | Current Semester: {student_profile.current_semester}.\n\n"
        f"--- REAL-TIME ACADEMIC CORE MEMORY ---\n"
        f"- Data Science Eligibility: {eligibility}% Ready\n"
        f"- ML Predicted Track: {career_track}\n"
        f"- Neural Network Predicted CGPA: {predicted_cgpa}\n"
        f"\n--- STUDENT PRACTICAL LOGS & WEAKNESSES ---\n"
        f"{student_gaps_context if student_gaps_context else 'No logs submitted yet.'}\n"
        f"-----------------------------------------\n\n"
        f"CHALLENGE THE STUDENT:\n"
        f"1. Talk like a friendly human faculty member in a mix of Bengali and English (Banglish).\n"
        f"2. Nudge the student about their weak points (e.g., CV building, LinkedIn presence, Presentation slides, English speaking, or coding blocks) depending on what they lack.\n"
        f"3. Keep your response concise, sharp, and highly motivating."
    )

    # ৪. টাস্ক ও মডেল রাউটিং
    has_image = bool(image_data_base64)
    task_category, target_model = detect_task_category(user_message, has_image)
    
    # --- গুগল ডিরেক্ট জেমিনি রুট (যদি ইমেজ থাকে এবং গুগল কী ভ্যালিড থাকে) ---
    if task_category == "VISION" and google_key:
        # ওপেনরাউটার ভিশন যদি কোনো কারণে রেসপন্স না করে, সরাসরি গুগলে ব্যাকআপ হিট করবে
        google_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={google_key}"
        google_payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_instruction}\n\nUser Question: {user_message}"},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_data_base64
                            }
                        }
                    ]
                }
            ]
        }
        try:
            res = requests.post(google_url, json=google_payload, timeout=15)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            pass # গুগলে সমস্যা হলে অটোমেটিক নিচের ওপেনরাউটার ভিশন মডেলে চলে যাবে

    # --- ওপেনরাউটার ফ্রি ক্লাস্টার রুট (মাল্টি-মডেল অটো ফেলব্যাক সহ) ---
    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://127.0.0.1:8000"
    }

    # আপনার চার্ট অনুযায়ী টাস্ক ওয়াইজ ব্যাকআপ মডেল চেইন
    fallback_models = {
        "GENERAL": ["openai/gpt-oss-20b:free", "meta-llama/llama-3.3-70b-instruct:free", "openrouter/free"],
        "CODING": ["qwen/qwen3-coder:free", "poolside/laguna-m.1:free"],
        "REASONING": ["nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free", "nousresearch/hermes-3-llama-3.1-405b:free"],
        "VISION": ["nex-agi/nex-n2-pro:free", "nvidia/nemotron-nano-12b-v2-vl:free"]
    }

    models_to_execute = fallback_models.get(task_category, ["openrouter/free"])
    
    # কন্টেন্ট স্ট্রাকচার রেডি করা (টেক্সট + ইমেজ হ্যান্ডলিং)
    messages_content = [{"type": "text", "text": user_message}]
    if image_data_base64 and task_category == "VISION":
        messages_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_data_base64}"}
        })

    for model in models_to_execute:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": messages_content}
            ],
            "temperature": 0.6,
            "max_tokens": 1200
        }
        try:
            response = requests.post(openrouter_url, headers=headers, data=json.dumps(payload), timeout=12)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
        except Exception:
            continue

    return "নুবটিকে হাইব্রিড সার্ভার ক্লাস্টারে অতিরিক্ত ট্রাফিকের কারণে রেসপন্স জেনারেট করা যায়নি। আবার চেষ্টা করুন।"