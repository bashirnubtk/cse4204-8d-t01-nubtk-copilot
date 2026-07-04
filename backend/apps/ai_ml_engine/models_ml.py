import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from apps.academics.models import StudentResult
# আপনার তৈরি করা নতুন মডেলটিকে এখানে ইম্পোর্ট করা হলো
from apps.ai_ml_engine.models import MLPerformancePrediction

def train_and_predict_career_path(student_profile):
    """
    পয়েন্ট ৫.৩, ৫.৪ ও ৫.৫: Decision Tree এবং SVM অ্যালগরিদমের সমন্বয়ে
    স্টুডেন্টের একাডেমিক পারফরম্যান্স প্যাটার্ন ক্লাসিফিকেশন, ক্যারিয়ার ট্র্যাক প্রেডিকশন
    এবং আউটপুটটি সরাসরি MLPerformancePrediction মডেলে সেভ করা।
    """
    # ১. থিসিসের জন্য ডামি বা বেস ট্রেনিং ডেটাসেট (ফিচার্স: [Theory, Lab, Resource Clicks])
    # লেবেল: 0 = Software Engineering, 1 = Data Science / ML, 2 = Cyber Security
    X_train = np.array([
        [85, 90, 80], # স্টুডেন্ট ১: ল্যাব ও টুলস ভালো -> Data Science
        [90, 75, 40], # স্টুডেন্ট ২: থিওরি খুব ভালো -> Software Eng
        [70, 70, 90], # St ৩: টুলস ও রিসোর্সে অনেক বেশি ক্লিক -> Cyber Security
        [50, 60, 30], # কম পারফরম্যান্স -> Software Eng (General)
        [80, 85, 70], # ব্যালেন্সড -> Data Science
        [65, 75, 85] # টুলস ও প্র্যাকটিক্যাল বেশি -> Cyber Security
    ])
    y_train = np.array([1, 0, 2, 0, 1, 2]) # রেসপেক্টিভ ক্যারিয়ার লেবেল

    # ২. দুটি মডেলকে ট্রেইন (Fit) করা
    dt_model = DecisionTreeClassifier(criterion='entropy', max_depth=3, random_state=42)
    dt_model.fit(X_train, y_train)

    svm_model = SVC(kernel='linear', probability=True, random_state=42)
    svm_model.fit(X_train, y_train)

    # ৩. ডাটাবেজ থেকে বর্তমান স্টুডেন্টের রিয়েল-টাইম ফিচার ভেক্টর কালেক্ট করা
    results = StudentResult.objects.filter(student_profile=student_profile)

    if not results.exists():
        return {
            "predicted_track": "Evaluating (Needs Marks)",
            "confidence": "0.0%",
            "algorithm_used": "N/A",
            "db_status": "Not Saved - No Results Found"
        }

    # স্টুডেন্টের রিয়েল ডেটা প্রসেসিং
    avg_theory = float(sum([r.class_test_mark + r.final_exam_mark for r in results])) / results.count()
    avg_lab = float(sum([r.quiz_mark + r.attendance_percentage for r in results])) / results.count()

    total_clicks = 0
    if hasattr(student_profile.user, 'resourcehub_set'):
        total_clicks = sum([res.click_count for res in student_profile.user.resourcehub_set.all()])

    # টেস্ট ভেক্টর রেডি করা [Theory, Lab, Clicks]
    student_features = np.array([[avg_theory, avg_lab, total_clicks]])

    # ৪. প্রেডিকশন এবং কনফিডেন্স স্কোর বের করা
    dt_pred = dt_model.predict(student_features)[0]
    svm_proba = svm_model.predict_proba(student_features)[0]

    # ক্যারিয়ার ম্যাপিং ডিকশনারি
    career_map = {0: "Software Engineering", 1: "Data Science & Machine Learning", 2: "Cyber Security & Infra"}

    # থিসিস রিপোর্টের জন্য ডিসিশন ট্রি ও এসভিএম এর কম্বাইন্ড প্রেডিকশন সিঙ্ক
    final_prediction = career_map.get(dt_pred, "General IT")
    confidence_score = round(float(np.max(svm_proba) * 100), 2)

    # =======================================================
    # 🎯 পয়েন্ট ৫.৫: মডেলে ডেটা রিয়েল-টাইম সেভ বা আপডেট করার লজিক
    # =======================================================
    prediction_obj, created = MLPerformancePrediction.objects.get_or_create(student=student_profile)
    prediction_obj.readiness_score = confidence_score # এসভিএম কনফিডেন্স স্কোরকে রেডিনেস হিসেবে সেভ করা
    # predicted_cgpa টি আমরা পরবর্তী ধাপ ৬-এ টেনসরফ্লো দিয়ে আপডেট করব, আপাতত বেস কারেন্ট সিজিপিএ রাখা হলো
    prediction_obj.predicted_cgpa = float(student_profile.current_cgpa) if student_profile.current_cgpa else 0.0
    prediction_obj.save()

    return {
        "predicted_track": final_prediction,
        "confidence": f"{confidence_score}%",
        "algorithm_used": "Decision Tree (Entropy) + SVM Hybrid",
        "db_status": "Saved to MLPerformancePrediction Table"
    }