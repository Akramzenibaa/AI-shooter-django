import os
from pathlib import Path
import dj_database_url
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
# Ensure localhost and default domain are always allowed
ALLOWED_HOSTS += ['localhost', '127.0.0.1', 'aishooter.lbahi.digital']
# Remove duplicates and empty strings
ALLOWED_HOSTS = list(set([host.strip() for host in ALLOWED_HOSTS if host.strip()]))

CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
CSRF_TRUSTED_ORIGINS += ['http://localhost:5500', 'https://aishooter.lbahi.digital']
CSRF_TRUSTED_ORIGINS = list(set([origin.strip() for origin in CSRF_TRUSTED_ORIGINS if origin.strip()]))


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'cloudinary',
    'django_huey',

    # Local apps
    'apps.core',
    'apps.accounts',
    'apps.images',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'apps.accounts.middleware.PhoneMandatoryMiddleware',
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


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

# Advanced Connection Pooling (Postgres only)
# Disabled - Django's built-in connection pooling via conn_max_age is sufficient
# if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
#     DATABASES['default']['ENGINE'] = 'dj_db_conn_pool.backends.postgresql'
#     DATABASES['default']['POOL_OPTIONS'] = {
#         'POOL_SIZE': 10,
#         'MAX_OVERFLOW': 10,
#         'RECYCLE': 24 * 60 * 60, # 1 day
#     }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auth Settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/app/'
LOGOUT_REDIRECT_URL = '/app/'

# Email settings
# Use 'apps.core.email_backend.ResendEmailBackend' for Resend API
# Use 'django.core.mail.backends.smtp.EmailBackend' for SMTP (Gmail, etc.)
# Use 'django.core.mail.backends.console.EmailBackend' for development
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'AI Shooter <lbahidigital@gmail.com>')

# Allauth Google settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET', ''),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
# Skip email verification when connecting social accounts to existing accounts
SOCIALACCOUNT_EMAIL_REQUIRED = False
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

# Custom adapters to handle account connections without verification
ACCOUNT_ADAPTER = 'apps.accounts.adapter.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'apps.accounts.adapter.CustomSocialAccountAdapter'
ACCOUNT_SIGNUP_FORM_CLASS = 'apps.accounts.forms.CustomSignupForm'

# Google AI Studio
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')

# Security Settings for Reverse Proxy (Coolify/Traefik)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# ACCOUNTS - Force HTTPS
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# Cloudinary Settings
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET', ''),
}

# Polar.sh Settings
POLAR_ACCESS_TOKEN = os.getenv('POLAR_ACCESS_TOKEN', 'polar_oat_7eLqMiNnvaMblWwixLDOf9ybmEQHX0haR4aOr0XkMf3')
POLAR_WEBHOOK_SECRET = os.getenv('POLAR_WEBHOOK_SECRET', 'polar_whs_XxkXxN90ei8YlW5qGu7oI1KDeEwQFjQVJqrcV3rW3RZ')
POLAR_ENVIRONMENT = os.getenv('POLAR_ENVIRONMENT', 'production') # 'production' or 'sandbox'
# Mapping Polar product IDs to plans/credits
POLAR_PRODUCT_MAP = {
    # Subscriptions
    'e404b075-4eb7-43c9-8029-82db2e9d2a68': {'plan': 'starter', 'credits': 40}, # Starter Shop
    '6757d539-dcc5-4b21-8283-51ff87158ee9': {'plan': 'growth', 'credits': 140}, # Growth Brand
    '77501b94-f393-4865-ad02-4e26cfb9e160': {'plan': 'agency', 'credits': 320}, # Agency Elite

    # Credit Packs
    'dbc85dc0-15f0-4264-8274-1e34e72c1926': {'credits': 10},  # Trial Pack
    '18421782-506d-4afa-8783-94a1260da915': {'credits': 30},  # Studio Pack
    '6f3b62e4-447b-44c0-bf7c-342e9b1bc264': {'credits': 100}, # Pro Pack
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
# Huey Configuration (Background Tasks)
DJANGO_HUEY = {
    'default': 'default',
    'queues': {
        'default': {
            'huey_class': 'huey.SqliteHuey',
            'filename': os.path.join(BASE_DIR, 'db.huey'),
            'results': True,
            'store_none': False,
            'immediate': False,
            'consumer': {
                'workers': 2,
                'worker_type': 'thread',
            },
        }
    }
}
