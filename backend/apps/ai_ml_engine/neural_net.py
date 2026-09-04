import os
import numpy as np
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # টেনসরফ্লোর অতিরিক্ত ওয়ার্নিং হাইড করার জন্য
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from apps.academics.models import StudentResult
from apps.ai_ml_engine.models import MLPerformancePrediction

def predict_future_cgpa_with_nn(student_profile):
    """
    পয়েন্ট ৬.৪: ৩-লেয়ার বিশিষ্ট কৃত্রিম নিউরাল নেটওয়ার্ক (Artificial Neural Network - ANN)
    যা স্টুডেন্টের কারেন্ট একাডেমিক ট্র্যাক থেকে তার ফিউচার CGPA প্রেডিক্ট করে।
    """
    # ১. নিউরাল নেটওয়ার্ক ট্রেইনিংয়ের জন্য ডামি ম্যাট্রিক্স ডেটাসেট
    # ইনপুট ফিচার্স (X): [Current_CGPA, Attendance_Avg, Resource_Clicks]
    X_train = np.array([
        [4.00, 95.0, 50],
        [3.50, 85.0, 30],
        [3.00, 75.0, 20],
        [2.50, 65.0, 10],
        [3.80, 90.0, 45],
        [2.80, 70.0, 15]
    ], dtype=np.float32)

    # টার্গেট ভ্যালু (y): এক্সপেক্টেড ফিউচার সেমিস্টার CGPA
    y_train = np.array([4.00, 3.60, 3.10, 2.40, 3.85, 2.70], dtype=np.float32)

    # ২. ৩-লেয়ার কাস্টম নিউরাল নেটওয়ার্ক আর্কিটেকচার বিল্ডিং
    model = Sequential([
        Dense(8, input_dim=3, activation='relu', name='Input_Hidden_Layer_1'), # প্রথম হিডেন লেয়ার (ReLU)
        Dense(4, activation='relu', name='Hidden_Layer_2'), # দ্বিতীয় হিডেন লেয়ার (ReLU)
        Dense(1, activation='linear', name='Output_Regression_Layer') # আউটপুট লিনিয়ার রিগ্রেশন লেয়ার
    ])

    # ৩. মডেল কম্পাইলেশন (Adam অপ্টিমাইজার এবং Mean Squared Error লস ফাংশন)
    model.compile(optimizer=Adam(learning_rate=0.01), loss='mse')

    # মডেল ফিটিং (ব্যাকপ্রোপাগেশন এবং ৫০টি ইপোকের ট্রেইনিং রান)
    model.fit(X_train, y_train, epochs=50, verbose=0)

    # ৪. ডাটাবেজ থেকে স্টুডেন্টের লাইভ প্যারামিটারগুলো কালেক্ট করা
    results = StudentResult.objects.filter(student_profile=student_profile)
    current_cgpa = float(student_profile.current_cgpa) if student_profile.current_cgpa else 0.0

    avg_attendance = 0.0
    if results.exists():
        avg_attendance = float(sum([r.attendance_percentage for r in results])) / results.count()

    total_clicks = 0
    if hasattr(student_profile.user, 'resourcehub_set'):
        total_clicks = sum([res.click_count for res in student_profile.user.resourcehub_set.all()])

    # কারেন্ট স্টুডেন্টের রিয়েল টেস্ট ইনপুট ভেক্টর
    live_input = np.array([[current_cgpa, avg_attendance, total_clicks]], dtype=np.float32)

    # ৫. নিউরাল নেটওয়ার্ক ফরওয়ার্ড পাস প্রেডিকশন
    raw_prediction = model.predict(live_input, verbose=0)
    predicted_value = round(float(raw_prediction[0][0]), 2)

    # সিজিপিএ বাউন্ডারি প্রোটেকশন (৪.০০ এর বেশি বা ০.০০ এর নিচে যেন না যায়)
    if predicted_value > 4.00: predicted_value = 4.00
    if predicted_value < 0.00: predicted_value = 0.00

    # =======================================================
    # 🎯 আপনার তৈরি করা MLPerformancePrediction টেবিলে সেভ করা
    # =======================================================
    prediction_obj, created = MLPerformancePrediction.objects.get_or_create(student=student_profile)
    prediction_obj.predicted_cgpa = predicted_value
    prediction_obj.save()

    return {
        "predicted_future_cgpa": predicted_value,
        "nn_architecture": "3-Layer Multi-Layer Perceptron (MLP)",
        "loss_function": "MSE",
        "status": "Synchronized with DB"
    }