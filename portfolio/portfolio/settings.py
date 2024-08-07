"""
Django settings for portfolio project.

Generated by 'django-admin startproject' using Django 5.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)


import io
import os
import environ
from pathlib import Path
from google.cloud import secretmanager


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Set default environment variables
env = environ.Env(
    # Django
    DEBUG=(bool, True),
    SECRET_KEY=(str, ""),
    STATIC_ROOT=(str, "static"),
    OCR_SESSION_TRIES=(int, 3),
    CMMT_SESSION_TRIES=(int, 5),
    # Langchain
    RAW_DATA_PATH=(str, "./static_base/data"),
    TOP_K=(int, 4),
    FETCH_K=(int, 20),
    LAMBDA_MULTIPLIER=(float, 0.5),
    CHUNK_SIZE=(int, 4000),
    CHUNK_OVERLAP=(int, 200),
    EMBEDDING_TYPE=(str, "text-embedding-3-large"),
    SEARCH_TYPE=(str, "similarity"),
    DOCUMENT_SEPARATOR=(str, "\n\n"),
    LLM_MODEL_NAME=(str, "gpt-3.5-turbo"),
    LLM_TEMPERATURE=(float, 1.0),
    LLM_MAX_TOKEN_LENGTH=(int, None),
    LLM_TOP_P=(float, 1.0),
    LLM_PRESENCE_PENALTY=(float, 0.0),
    LLM_FREQUENCY_PENALTY=(float, 0.0),
    LLM_RAG_PROMPT_NAME=(str, "portfolio-rag-prompt"),
    LLM_AGENT_MAX_ITERATIONS=(int, 5),
    # Langsmith
    LANGCHAIN_TRACING_V2=(bool, True),
    LANGCHAIN_ENDPOINT=(str, "https://api.smith.langchain.com"),
    LANGCHAIN_API_KEY=(str, ""),
    LANGCHAIN_PROJECT=(str, "Portfolio"),
    # Pinecone
    PINECONE_API_KEY=(str, ""),
    PINECONE_INDEX_NAME=(str, "langchain"),
    # GCP
    SETTINGS_NAME=(str, "portfolio_settings"),
    SECRET_MANAGER_VERSION=(str, "4"),
    # AWS
    AWS_ACCESS_KEY_ID=(str, ""),
    AWS_SECRET_ACCESS_KEY=(str, ""),
    AWS_SES_REGION_NAME=(str, "us-west-2"),
    AWS_SES_REGION_ENDPOINT=(str, "email.us-west-2.amazonaws.com"),
)
env_file = os.path.join(BASE_DIR, ".env")

# Load environment variables from file or secret manager
if os.path.exists(env_file):
    env.read_env(env_file)
elif os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{env('SETTINGS_NAME')}/versions/{env('SECRET_MANAGER_VERSION')}"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")
    env.read_env(io.StringIO(payload))
else:
    raise Exception("No environment file or secret manager found.")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party
    'corsheaders',
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
    'corsheaders.middleware.CorsMiddleware',
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

CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS = [
    "https://personal-project-381802.wl.r.appspot.com", "https://kamath.work"]

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

docker run -d --name postgres -p 5499:5432 \
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
#         'NAME': env("PGDATABASE"),
#         'USER': env("PGUSER"),
#         'PASSWORD': env("PGPASSWORD"),
#         'HOST': env("PGHOST"),
#         'PORT': env("PGPORT")
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
STATIC_ROOT = env("STATIC_ROOT")

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

# Email settings
EMAIL_BACKEND = 'django_ses.SESBackend'
DEFAULT_FROM_EMAIL = "no-reply@kamath.work"
DEFAULT_NIKHIL_EMAIL = "nikhilbo@kamath.work"
DEFAULT_EMAIL_SUBJECT = "Nikhil Bola Kamath - Contact Form"

# AWS settings
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_SES_REGION_NAME = env("AWS_SES_REGION_NAME")
AWS_SES_REGION_ENDPOINT = env("AWS_SES_REGION_ENDPOINT")

# Django cache and session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
OCR_SESSION_KEY_TRIES = ["ocr_session_tries", env("OCR_SESSION_TRIES")]
CMMT_SESSION_KEY_TRIES = ["cmmt_session_tries", env("CMMT_SESSION_TRIES")]
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 60 * 60 * 3 # 3 hours

# Service APIs
# OCR
OCR_GCLOUD_RUN_API = "https://ocr-zwqz52dqpa-uw.a.run.app"
# CM-MT
CM_MT_GCLOUD_RUN_API = "https://cmmt-zwqz52dqpa-uw.a.run.app"

# Langchain settings
RAW_DATA_PATH = env("RAW_DATA_PATH")
TOP_K = env("TOP_K")
FETCH_K = env("FETCH_K")
LAMBDA_MULTIPLIER = env("LAMBDA_MULTIPLIER")
CHUNK_SIZE = env("CHUNK_SIZE")
CHUNK_OVERLAP = env("CHUNK_OVERLAP")
EMBEDDING_TYPE = env("EMBEDDING_TYPE")
SEARCH_TYPE = env("SEARCH_TYPE")
DOCUMENT_SEPARATOR = env("DOCUMENT_SEPARATOR")
LLM_MODEL_NAME = env("LLM_MODEL_NAME")
LLM_TEMPERATURE = env("LLM_TEMPERATURE")
LLM_MAX_TOKEN_LENGTH = env("LLM_MAX_TOKEN_LENGTH")
LLM_TOP_P = env("LLM_TOP_P")
LLM_PRESENCE_PENALTY = env("LLM_PRESENCE_PENALTY")
LLM_FREQUENCY_PENALTY = env("LLM_FREQUENCY_PENALTY")
LLM_RAG_PROMPT_NAME = env("LLM_RAG_PROMPT_NAME")
LLM_AGENT_MAX_ITERATIONS = env("LLM_AGENT_MAX_ITERATIONS")

# Langchain tool setting
REGISTER_SEND_EMAIL_RETURN = "Your message has been registered for sending."

# Pinecone settings
PINECONE_API_KEY = env("PINECONE_API_KEY")
PINECONE_INDEX_NAME = env("PINECONE_INDEX_NAME")
PINECONE_INDEX_CONFIG = {
    "text-embedding-3-large": {
        "dimension": 3072,
        "metric": "cosine"
    }
}