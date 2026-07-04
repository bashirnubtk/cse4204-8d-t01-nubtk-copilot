import numpy as np
import pandas as pd
from apps.academics.models import StudentResult

def calculate_global_eligibility(student_profile):
    """
    পয়েন্ট ৪.৩ ও ৪.৪: NumPy এবং Pandas ব্যবহার করে গ্লোবাল এলিজিবিলিটি স্কোর ক্যালকুলেটর।
    এটি স্টুডেন্টের কারেন্ট একাডেমিক ট্র্যাক এবং রিসোর্স ক্লিক প্যাটার্ন বিশ্লেষণ করে।
    """
    # ১. গ্লোবাল জব মার্কেটের বেঞ্চমার্ক (আদর্শ স্কোর ১০০ এর মধ্যে)
    # [Theory/Conceptual, Hands-on Lab/Coding, Tools/Resource Utilization]
    GLOBAL_BENCHMARK = np.array([80.0, 85.0, 75.0])
    
    # ২. ডাটাবেজ থেকে স্টুডেন্টের রেজাল্ট ডেটা ফেচ করা (Pandas DataFrame এ রূপান্তর)
    results = StudentResult.objects.filter(student_profile=student_profile)
    
    # =======================================================
    # 🎯 ধাপ ৪.৩ (সংশোধিত): আগাম ৪০% স্কোর ফিক্স করা
    # =======================================================
    if not results.exists():
        # কোনো একাডেমিক ডেটা না থাকলে স্কোর ০.০% হবে, আগাম কোনো নম্বর থাকবে না
        return {
            "eligibility_percentage": 0.0, 
            "student_vector": [0.0, 0.0, 0.0], 
            "benchmark_vector": GLOBAL_BENCHMARK.tolist()
        }
        
    data = []
    for r in results:
        data.append({
            'theory': float(r.class_test_mark + r.final_exam_mark), # থিওরি মার্কস
            'lab': float(r.quiz_mark + r.attendance_percentage),    # ল্যাব ও প্র্যাকটিক্যাল মার্কস
        })
    
    df = pd.DataFrame(data)
    
    # ৩. স্টুডেন্টের গড়ে থিওরি ও ল্যাব পারফরম্যান্স বের করা (NumPy ভেক্টর)
    avg_theory = df['theory'].mean() if not df.empty else 0
    avg_lab = df['lab'].mean() if not df.empty else 0
    
    # রিসোর্স হাবের ক্লিক অ্যাক্টিভিটি থেকে টুলস ব্যবহারের স্কোর জেনারেট (সর্বোচ্চ ১০০)
    # স্টুডেন্ট প্রোফাইলের সাথে রিলেটেড ইউজারের রিসোর্স ক্লিক কাউন্ট সামারি করা
    total_clicks = 0
    if hasattr(student_profile.user, 'resourcehub_set'):
        total_clicks = sum([res.click_count for res in student_profile.user.resourcehub_set.all()])
    
    tools_score = min(total_clicks * 5, 100) # প্রতি ক্লিকে ৫ পয়েন্ট, সর্বোচ্চ ১০০
    
    # স্টুডেন্ট প্রোফাইল ভেক্টর তৈরি
    student_vector = np.array([avg_theory, avg_lab, tools_score])
    
    # ৪. গাণিতিক সূত্র (Vector Cosine Similarity & Dot Product)
    # গ্লোবাল বেঞ্চমার্কের সাথে স্টুডেন্টের ভেক্টরের সামঞ্জস্যতা পরিমাপ
    dot_product = np.dot(student_vector, GLOBAL_BENCHMARK)
    norm_student = np.linalg.norm(student_vector)
    norm_benchmark = np.linalg.norm(GLOBAL_BENCHMARK)
    
    if norm_student == 0 or norm_benchmark == 0:
        similarity = 0.0
    else:
        similarity = dot_product / (norm_student * norm_benchmark)
        
    # পার্সেন্টেজ স্কোর (০ থেকে ১০০ এর মধ্যে স্কেলিং)
    eligibility_percentage = round(float(similarity * 100), 2)
    
    # ওয়ান-ক্লিক সেফটি মেকানিজম (১০০ এর বেশি যেন না হয়)
    if eligibility_percentage > 100: 
        eligibility_percentage = 100.0
    
    return {
        "eligibility_percentage": eligibility_percentage,
        "student_vector": student_vector.tolist(),
        "benchmark_vector": GLOBAL_BENCHMARK.tolist()
    }