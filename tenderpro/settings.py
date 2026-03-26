"""
Django settings for tenderpro project.
"""

from pathlib import Path
import os
import dj_database_url

# ==============================
# BASE DIR
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================
# SECURITY
# ==============================
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']  # change later after deployment

# 🔥 Fix for Render (HTTPS handling)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# ==============================
# APPLICATIONS
# ==============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts',
    'tenders',
    'bids',
    'dashboard',
]


# ==============================
# MIDDLEWARE
# ==============================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # 🔥 WhiteNoise for static files
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ==============================
# URL CONFIG
# ==============================
ROOT_URLCONF = 'tenderpro.urls'


# ==============================
# TEMPLATES
# ==============================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ==============================
# WSGI
# ==============================
WSGI_APPLICATION = 'tenderpro.wsgi.application'


# ==============================
# DATABASE (Render-ready)
# ==============================
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}


# ==============================
# PASSWORD VALIDATION
# ==============================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==============================
# INTERNATIONALIZATION
# ==============================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ==============================
# STATIC FILES (VERY IMPORTANT)
# ==============================

# Base URL for static files
STATIC_URL = '/static/'

# Folder where Django will collect static files for production (Render)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 📌 THIS is where your custom static files live (css, js, images)
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# WhiteNoise (serves static files in production)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ==============================
# MEDIA FILES
# ==============================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ==============================
# DEFAULT PRIMARY KEY
# ==============================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================
# EMAIL CONFIGURATION
# ==============================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER