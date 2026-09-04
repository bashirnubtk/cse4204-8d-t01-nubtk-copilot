<<<<<<< HEAD
import requests
import json
from django.conf import settings
import environ

env = environ.Env()

class OpenRouterClient:
    def __init__(self):
        self.api_key = env('OPENROUTER_API_KEY', default='')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def analyze_student_skills(self, skill_list, industry_target="Web Development"):
        if not self.api_key:
            return {"error": "OpenRouter API Key mapping is missing inside environment setup."}
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "NUBTK Copilot ERP"
        }
        
        prompt = f"Analyze the following skills for a student aiming for a career in {industry_target}: {', '.join(skill_list)}. Provide actionable gaps and recommendations as a strict JSON format containing 'gaps' and 'recommendations' keys."
        
        # জেমিনির বদলে ওপেনরাউটারের ফ্রি মডেল বসানো হলো
        payload = {
            "model": "qwen/qwen3-coder:free", 
            "messages": [
                {"role": "system", "content": "You are an expert tech career mentor focusing on Bangladeshi university graduates."},
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, data=json.dumps(payload), timeout=12)
            if response.status_code == 200:
                result = response.json()
                ai_content = result['choices'][0]['message']['content']
                return json.loads(ai_content)
            return {"error": f"API returned status code {response.status_code}", "details": response.text}
        except Exception as e:
=======
import requests
import json
from django.conf import settings
import environ

env = environ.Env()

class OpenRouterClient:
    def __init__(self):
        self.api_key = env('OPENROUTER_API_KEY', default='')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def analyze_student_skills(self, skill_list, industry_target="Web Development"):
        if not self.api_key:
            return {"error": "OpenRouter API Key mapping is missing inside environment setup."}
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "NUBTK Copilot ERP"
        }
        
        prompt = f"Analyze the following skills for a student aiming for a career in {industry_target}: {', '.join(skill_list)}. Provide actionable gaps and recommendations as a strict JSON format containing 'gaps' and 'recommendations' keys."
        
        # জেমিনির বদলে ওপেনরাউটারের ফ্রি মডেল বসানো হলো
        payload = {
            "model": "qwen/qwen3-coder:free", 
            "messages": [
                {"role": "system", "content": "You are an expert tech career mentor focusing on Bangladeshi university graduates."},
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, data=json.dumps(payload), timeout=12)
            if response.status_code == 200:
                result = response.json()
                ai_content = result['choices'][0]['message']['content']
                return json.loads(ai_content)
            return {"error": f"API returned status code {response.status_code}", "details": response.text}
        except Exception as e:
>>>>>>> cc3d22ff42f8869ce0a4aa7e99e905cb0f74f89f
            return {"error": str(e)}