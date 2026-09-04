# Auto-generated file
from backend.apps.students.models import StudentProfile
from.openrouter_api import ask_openrouter

def analyze_student_gaps(student_id):
    try:
        student = StudentProfile.objects.get(student_id=student_id)
        weak_subjects = []

        for semester in student.semesters.all():
            for subject in semester.subjects.filter(gpa__lt=2.5):
                weak_subjects.append({
                    "code": subject.subject_code,
                    "name": subject.subject_name,
                    "gpa": subject.gpa,
                    "semester": semester.semester_no
                })

        if not weak_subjects:
            return "তোমার কোনো সাবজেক্টে Weakness নাই। CGPA ভালো রাখো।"

        prompt = f"""
        তুমি NUBTK এর CSE ডিপার্টমেন্টের একজন এডভাইজার।
        স্টুডেন্ট: {student.name}, ID: {student.student_id}
        দুর্বল সাবজেক্টগুলো: {weak_subjects}

        এই স্টুডেন্টকে বাংলায় বন্ধুর মতো বুঝাও:
        1. এই সাবজেক্টগুলোতে খারাপ করার কারণে জব মার্কেটে কী সমস্যা হবে?
        2. কেন এই স্কিলগুলো শিখতেই হবে?
        3. কীভাবে শিখবে, 3টা স্পেসিফিক স্টেপ দাও।
        4. মোটিভেট করো।
        """
        return ask_openrouter(prompt)

    except StudentProfile.DoesNotExist:
        return "Student ID খুঁজে পাওয়া যায়নি।"