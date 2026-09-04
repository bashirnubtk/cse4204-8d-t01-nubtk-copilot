import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime

class User(AbstractUser):
    """
    Custom user model enabling secure authentication via unique Email.
    """
    is_student = models.BooleanField(default=False)
    is_university_admin = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class StudentProfile(models.Model):
    """
    Main repository storing application state, active status, marks data, and metrics.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved & Active'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    
    # Selection Parameters
    ssc_gpa = models.FloatField(default=0.0)
    hsc_gpa = models.FloatField(default=0.0)
    admission_score_percentage = models.FloatField(default=0.0)
    
    # New & Updated Fields
    department = models.CharField(max_length=50, default="CSE")
    profile_picture = models.ImageField(upload_to='students/profiles/', null=True, blank=True)
    
    # System Managed Identifiers
    digital_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Internal Performance Trackers
    current_semester = models.IntegerField(default=1)
    class_test_mark = models.FloatField(default=0.0)
    quiz_mark = models.FloatField(default=0.0)
    attendance_percentage = models.FloatField(default=0.0)
    current_cgpa = models.FloatField(default=0.0)
    
    # AI OpenRouter Tracking fields
    ai_career_guideline = models.TextField(blank=True, null=True)
    industry_readiness_percentage = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        ✅ রেজিস্ট্রেশনের সময়ই NUBTK-2026-XXXX আইডি বানাবে
        """
        # প্রথমবার সেভ হলে digital_id বানাও
        if not self.digital_id:
            current_year = datetime.now().year
            # শেষ ID বের করো
            last_profile = StudentProfile.objects.order_by('-id').first()
            next_id = 1859 if not last_profile else 1859 + last_profile.id
            self.digital_id = f"NUBTK-{current_year}-{next_id}"
            
            # ইউজারের username ও পাসওয়ার্ড digital_id দিয়ে আপডেট করো
            if self.user:
                self.user.username = self.digital_id
                self.user.set_password(self.digital_id)  # টেম্প পাসওয়ার্ড
                self.user.save()

        if self.ssc_gpa and self.hsc_gpa:
            self.admission_score_percentage = ((self.ssc_gpa * 0.4) + (self.hsc_gpa * 0.6)) * 20
        
        super().save(*args, **kwargs)

    def execute_approval_sequence(self):
        """
        ✅ অ্যাপ্রুভ করলে সঠিক ইমেইল যাবে
        """
        if not self.digital_id:
            self.save()  # digital_id বানাও
        
        self.status = 'APPROVED'
        self.save()
        
        # ইউজার অ্যাক্টিভ করো
        associated_user = self.user
        associated_user.is_active = True
        associated_user.save()

        # ✅ প্রফেশনাল ইমেইল ফরম্যাট
        subject = f'Official Admission Approval - ID {self.digital_id}'
        body_message = f"""Dear {self.student_name},

Congratulations! Your admission application has been approved by NUBTK Academic Authority.

Your Access Credentials:

Login Email: {associated_user.email}
Secure Portal Password: {self.digital_id}
Digital Enrollment ID: {self.digital_id}

Login URL: http://127.0.0.1:8000/portal/gateway/login/

Please keep this password confidential.

Best Regards,
NUBTK_ADMIN
Department of CSE
Northern University of Business and Technology, Khulna
"""
        try:
            send_mail(
                subject,
                body_message,
                'NUBTK_ADMIN <noreply@nubtk.edu.bd>',
                [associated_user.email],
                fail_silently=False,
            )
        except Exception as e:
            pass

    def __str__(self):
        return f"{self.student_name} ({self.status})"

class Course(models.Model):
    """
    Syllabus data storage component.
    """
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=255)  # ✅ এটাই ফাইনাল
    credits = models.FloatField(default=3.0)
    semester = models.IntegerField(default=1)
    department = models.CharField(max_length=100, default='CSE')  # ✅ এটাও লাগবে

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"

class StudentResult(models.Model):
    """
    Per student, per course, per semester detailed academic result.
    """
    student_profile = models.ForeignKey('StudentProfile', on_delete=models.CASCADE, related_name='academic_results')
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    semester = models.IntegerField()
    
    class_test_mark = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    quiz_mark = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    final_exam_mark = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    subject_cgpa = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student_profile', 'course', 'semester')
        verbose_name = "Student Result"
        verbose_name_plural = "Student Results"

    def __str__(self):
        return f"{self.student_profile.student_name} - {self.course.course_code} (Sem: {self.semester})"

class PaymentHistory(models.Model):
    """
    প্রতি সেমিস্টারের ৩টি ইনস্টলমেন্ট এবং লাইভ ট্র্যাকিংয়ের মূল ডাটাবেজ মডেল।
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
    ]
    
    student_profile = models.ForeignKey('StudentProfile', on_delete=models.CASCADE, related_name='payments')
    semester = models.IntegerField(default=1)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_profile.student_name} - {self.title} ({self.status})"

class ResourceHub(models.Model):
    """
    ধাপ ৮.১: অ্যাডমিন কর্তৃক আপলোড করা পড়াশোনার রিসোর্স এবং 
    স্টুডেন্টদের ক্লিক ট্র্যাকিংয়ের মূল ডাটাবেজ মডেল।
    """
    CATEGORY_CHOICES = [
        ('SOFTWARE', 'Software Engineering'),
        ('DATA_SCIENCE', 'Data Science & ML'),
        ('CYBER_SECURITY', 'Cyber Security'),
        ('GENERAL', 'General Academic'),
        # পুরনো ক্যাটাগরিগুলো রাখা হলো যাতে আগের ডাটা নষ্ট না হয়
        ('CLASSROOM', 'Classroom Resource / Lecture Notes'),
        ('DESKTOP_APP', 'Desktop Application'),
        ('MOBILE_APP', 'Mobile Application'),
        ('CODING_TOOL', 'Coding & ML Tools'),
        ('CRACK_SOFTWARE', 'Third-Party Software (Free/Crack)'),
        ('INTERVIEW_GUIDE', 'Interview & Career Guide'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='GENERAL')
    resource_url = models.URLField(max_length=500, blank=True, null=True)  # ✅ ধাপ ৮.১ নতুন ফিল্ড
    description = models.TextField(blank=True, null=True)
    external_link = models.URLField(max_length=500, blank=True, null=True)  # পুরনো ফিল্ড - ব্যাকওয়ার্ড কম্প্যাটিবিলিটি
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    click_count = models.IntegerField(default=0) # এই কাউন্টটি সরাসরি আমাদের এআই ভেক্টরে যুক্ত হয়
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # পুরনো এবং নতুন URL ফিল্ড সিঙ্ক রাখা - যাতে কোনো কোড ভাঙে না
        if self.resource_url and not self.external_link:
            self.external_link = self.resource_url
        elif self.external_link and not self.resource_url:
            self.resource_url = self.external_link
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"

class StudentPracticalLog(models.Model):
    """
    লেয়ার ১.১: প্রতিটা সাবজেক্টের বিপরীতে স্টুডেন্টের প্র্যাকটিক্যাল লার্নিং, 
    স্কিল গ্যাপ এবং সফট স্কিল ট্র্যাকিং মডেল।
    """
    student_profile = models.ForeignKey('StudentProfile', on_delete=models.CASCADE, related_name='practical_logs')
    subject_code = models.CharField(max_length=20) # যেমন: CSE-1103
    subject_name = models.CharField(max_length=200)
    
    # স্টুডেন্টের থেকে নেওয়া বাস্তব ভিত্তিক ৩টি কোর ইনফরমেশন
    tools_learned = models.TextField(blank=True, null=True, help_text="যেমন: VS Code, Git, MS PowerPoint")
    project_outcome = models.TextField(blank=True, null=True, help_text="এই সাবজেক্টে প্র্যাকটিক্যালি কী প্রজেক্ট বা কাজ করেছেন?")
    skill_gaps_declared = models.TextField(blank=True, null=True, help_text="আপনার কী কী গ্যাপ রয়ে গেছে? (যেমন: ইংরেজি বলা, স্লাইড বানানো, প্রেজেন্টেশন বা কোডিং)")
    
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student Practical Log"
        verbose_name_plural = "Student Practical Logs"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.student_profile.student_name} - {self.subject_code} Skill Log"