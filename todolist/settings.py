"""
Django settings for todolist project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from envparse import env
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR.joinpath('.env')

if ENV_PATH.exists() and ENV_PATH.is_file():
    env.read_envfile(ENV_PATH)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

SECRET_KEY = env('SECRET_KEY')

DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'social_django',
    'django_filters',
    'core',
    'goals',
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

ROOT_URLCONF = 'todolist.urls'

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

WSGI_APPLICATION = 'todolist.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST', default='127.0.0.1'),
        'PORT': env.int('POSTGRES_PORT', default=5432)
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'core.User'

# REST_FRAMEWORK = {
#     "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
#     "PAGE_SIZE": 4,
# }
# 'rest_framework.pagination.LimitOffsetPagination'

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR.joinpath('static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# VK OAUTH2 settings
# SOCIAL_AUTH_JSONFIELD_ENABLED = True
# SOCIAL_AUTH_JSONFIELD_CUSTOM = 'django.db.models.JSONField'
# SOCIAL_AUTH_VK_OAUTH2_KEY = env.str('VK_OAUTH_ID')
# SOCIAL_AUTH_VK_OAUTH2_SECRET = env.str('VK_OAUTH_SECRET_KEY')
# AUTHENTICATION_BACKENDS = (
#     'social_core.backends.vk.VKAppOAuth2',
#     'django.contrib.auth.backends.ModelBackend',
# )
# SOCIAL_AUTH_URL_NAMESPACE = 'social'
# SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
# SOCIAL_AUTH_LOGIN_ERROR_URL = '/login-error/'
# SOCIAL_AUTH_VK_OAUTH2_SCOPE = ['email']
# SOCIAL_AUTH_VK_EXTRA_DATA = [
#     ('email', 'email')
# ]
# SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/logged-in/'
# SOCIAL_AUTH_USER_MODEL = 'core.User'
