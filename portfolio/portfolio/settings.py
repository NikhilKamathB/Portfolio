"""
Django settings for portfolio project.

Generated by 'django-admin startproject' using Django 4.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get("DEBUG", 1)))

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party
    'django_summernote',
    # apps
    'home.apps.HomeConfig',
    'sdc.apps.SdcConfig',
    'ocr.apps.OcrConfig',
    'cm_mt.apps.CmMtConfig',
    'acnn.apps.AcnnConfig',
    'simpan.apps.SimpanConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ocr.middleware.OcrMiddleware',
    'cm_mt.middleware.CmmtMiddleware'
]

ROOT_URLCONF = 'portfolio.urls'

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

WSGI_APPLICATION = 'portfolio.wsgi.application'

CSRF_TRUSTED_ORIGINS = ['http://*', 'https://*']

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
# Use sqlite3.
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

'''
To install postgres using docker:

docker run -d --name postgres -p 5499:5432 \                                                                                                                   tyche@tyche
-e POSTGRES_USER=portfolio \
-e POSTGRES_PASSWORD=portfolio \
-e POSTGRES_DB=portfolio \
postgres:latest

'''
# Use postgres.
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': os.getenv('PGDATABASE', 'postgres'),
#         'USER': os.getenv('PGUSER', 'postgres'),
#         'PASSWORD': os.getenv('PGPASSWORD', 'postgres'),
#         'HOST': os.getenv('PGHOST', '127.0.0.1'),
#         'PORT': os.getenv('PGPORT', '5432'),
#     },
# }

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


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = '/static/'
STATIC_BASE = 'static_base'
STATICFILES_DIRS = [
        BASE_DIR / STATIC_BASE
    ]
STATIC_ROOT = os.getenv('STATIC_ROOT', "static")

# Media handling.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# site id
SITE_ID = 1

# Internal IPs
INTERNAL_IPS = ['127.0.0.1',]

# Summernote config
X_FRAME_OPTIONS = 'SAMEORIGIN'
SUMMERNOTE_CONFIG = {
    'disable_attachment': False,
    'summernote': {
            'toolbar': [
        ['style', ['bold', 'italic', 'underline', 'clear']],
        ['fontsize', ['fontsize']],
        ['color', ['color']],
        ['para', ['ul', 'ol', 'paragraph']],
        ['table', ['table']],
        ['insert', ['link', 'picture', 'video']],
        ['view', ['fullscreen', 'codeview', 'help']]
            ]
        }
    }

# Django session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
OCR_SESSION_KEY_TRIES = ["ocr_session_tries", 3]
CMMT_SESSION_KEY_TRIES = ["cmmt_session_tries", 7]
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 60 * 60 * 3 # 3 hours

# Langchain settings
RAW_DATA_PATH = os.getenv("RAW_DATA_PATH", "./static_base/data")
CHORMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./static_base/chroma_db")
CHUNK_SIZE = 4000
CHUNK_OVERLAP = 200
TOP_K = 5

# Service APIs
# OCR
OCR_GCLOUD_RUN_API = "https://ocr-zwqz52dqpa-uw.a.run.app"
# CM-MT
CM_MT_GCLOUD_RUN_API = "https://cmmt-zwqz52dqpa-uw.a.run.app"