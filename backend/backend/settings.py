# flake8: noqa
import os
from pathlib import Path
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')

DEBUG = os.getenv('DEBUG_MODE', 'False')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'rest_framework',
    'shortener',
    'djoser',
    "django_filters",
    'api',
    'recipes',
    'users',
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

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = { 
    'default': { 
        'ENGINE': 'django.db.backends.postgresql', 
        'NAME': os.getenv('POSTGRES_DB', 'foodgram'), 
        'USER': os.getenv('POSTGRES_USER', 'foodgram'), 
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''), 
        'HOST': os.getenv('DB_HOST', ''), 
        'PORT': os.getenv('DB_PORT', 5432) 
    }
}

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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}

DJOSER = {
    "LOGIN_FIELD": "email",
    "HIDE_USERS": False,
    "PERMISSIONS": {
        "resipe": ("api.permissions.IsAuthAdminAuthorOrReadOnly",),
        "recipe_list": ("api.permissions.IsAuthAdminAuthorOrReadOnly",),
        "user": ("api.permissions.IsAuthAdminAuthorOrReadOnly",),
        "user_list": ("api.permissions.IsAuthAdminAuthorOrReadOnly",),
    },
    "SERIALIZERS": {
        "user": "api.serializers.UserSerializer",
        "user_list": "api.serializers.UserSerializer",
        "current_user": "api.serializers.UserSerializer",
        "user_create": "api.serializers.UserCreateSerializer",
    },
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'collected_static'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.UserProfile'

CUSTOM_PAGE_SIZE = 10