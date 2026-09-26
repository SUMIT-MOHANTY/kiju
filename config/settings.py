import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # Default auto
# field for models

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

AUTH_USER_MODEL = "accounts.CustomUser"  # Custom user
# model with email as primary identifier

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
                'django.contrib.auth.context_processors.auth',  # Auth
                # context processors
    },
    {
                'django.contrib.messages.context_processors.messages',  #
                # Messages context processors
    },
    {
                'django.middleware.security.SecurityMiddleware',  # Security
                # middleware
    },
    {
                'django.contrib.sessions.middleware.SessionMiddleware',  #
                # Session middleware
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'auth.User'

# =============================================================================
# SECURITY HARDENING - Session & CSRF Protection
# =============================================================================

# Session Security Configuration
# Session expires after 30 minutes of inactivity
SESSION_COOKIE_AGE = 1800  # 30 minutes in seconds
SESSION_SAVE_EVERY_REQUEST = True  # Reset expiry on every request
SESSION_COOKIE_SECURE = True  # HTTPS only - cookies only sent over secure connections
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # Protect against CSRF in modern browsers

# CSRF Security Configuration
CSRF_COOKIE_SECURE = True  # HTTPS only in production
CSRF_COOKIE_HTTPONLY = False  # Must be accessible by JavaScript for HTMX compatibility
CSRF_COOKIE_SAMESITE = 'Lax'  # CSRF protection level

# Authentication Redirects
LOGIN_REDIRECT_URL = '/todos/'  # Redirect after successful login
LOGIN_URL = '/login/'  # URL for login_required decorator

# =============================================================================
# RATE LIMITING MIDDLEWARE
# =============================================================================
# IMPORTANT: To enable rate limiting, add 'apps.core.middleware.RateLimitMiddleware'
# to the MIDDLEWARE list after AuthenticationMiddleware:
#
# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'apps.core.middleware.RateLimitMiddleware',  # <-- ADD THIS LINE
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]
