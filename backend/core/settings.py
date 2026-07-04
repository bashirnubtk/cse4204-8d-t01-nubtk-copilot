import os
import sys
from pathlib import Path

# ==========================================
# 1. Base Directory and System Paths Setup (FIRST PRIORITY)
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if str(BASE_DIR) not in sys.path:
    sys.path.insert(1, str(BASE_DIR))

# ==========================================
# 2. Security and Environment Matrix
# ==========================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-master-copilot-production-key-2026')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

# ==========================================
# 3. Database Engine Configuration
# ==========================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ==========================================
# 4. Target Custom User Model Configuration (Crucial for Academics App)
# ==========================================
AUTH_USER_MODEL = 'academics.User'

# ==========================================
# 5. Core Operational Apps Register
# ==========================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Internal Custom Apps Matrix
    'apps.academics',
    'apps.portal_web',
    'apps.ai_mentor',
    'apps.ai_ml_engine',
    'apps.students',
]

# ==========================================
# 6. Middleware and Security Pipeline
# ==========================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

# ==========================================
# 7. Templates Layout Structure - FIXED
# ==========================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BACKEND_DIR, 'apps', 'portal_web', 'templates')],  # <-- এটা যোগ করছি
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ==========================================
# 8. Password Security Validators
# ==========================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==========================================
# 9. Internationalization and Timezone Matrix
# ==========================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

# ==========================================
# 10. Static and Dynamic Media Assets Management
# ==========================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BACKEND_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# 11. Secure Gmail SMTP Server Ingestion Setup (FINAL WORKING VERSION)
# ==========================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

env_file_path = BASE_DIR / '.env'

def get_env_variable(key, default=""):
    """ .env ফাইল থেকে সরাসরি সিকিউর ডেটা রিড করার ইউনিভার্সাল মেকানিজম """
    if env_file_path.exists():
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    k, v = line.strip().split('=', 1)
                    if k.strip() == key:
                        return v.strip()
    return os.environ.get(key, default)

EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER', 'alambashir257@gmail.com')
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = f"NUBTK Registrar <{EMAIL_HOST_USER}>"