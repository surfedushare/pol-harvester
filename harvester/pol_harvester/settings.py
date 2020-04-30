"""
Django settings for pol_harvester project.

Generated by 'django-admin startproject' using Django 1.11.15.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get git commit info to keep track of versions of data
GIT_COMMIT = os.environ.get('DJANGO_GIT_COMMIT', None)
if not GIT_COMMIT:
    raise ImproperlyConfigured('DJANGO_GIT_COMMIT variable has not been set to a git commit hash')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'm+2zzqoclh8b6um4%#k&(gw!!(=mmw&$y&u^14jkyt$t==p-$e')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get('DJANGO_DEBUG', "0")))

ALLOWED_HOSTS = [
    'localhost',
    '.surfpol.nl',
    '.surfcatalog.nl'
]
CORS_ORIGIN_WHITELIST = [
    'localhost:8080',
    'localhost:8000',
    '127.0.0.1:8080',
    'tagger.surfpol.nl'
]
SITE_ID = 1


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django_celery_results',

    'datagrowth',
    'pol_harvester',
    'edurep',
    'ims',
    'search',
    'media_site'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'pol_harvester.authentication.SearchBasicAuthMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pol_harvester.urls'

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

WSGI_APPLICATION = 'pol_harvester.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pol',
        'USER': os.environ.get('DJANGO_POSTGRES_USER', 'django'),
        'PASSWORD': os.environ.get('DJANGO_POSTGRES_PASSWORD', 'Yd36ewNjYBKY4MRUjmXMpaoHvxvR2Yqe') or None,
        'HOST': os.environ.get('POSTGRES_HOST', '127.0.0.1')
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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


# Basic Auth
# https://github.com/hirokiky/django-basicauth

username = os.environ.get("ELASTIC_SEARCH_USERNAME")
password = os.environ.get("ELASTIC_SEARCH_PASSWORD")
if not username or not password:
    raise ImproperlyConfigured("Username and/or password not specified for Basic Auth")
BASICAUTH_USERS = {
    username: password
}


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Logging
# https://docs.djangoproject.com/en/1.11/topics/logging/
LOGS_DIR = os.path.join(BASE_DIR, '..', 'logs')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'debug.log'),
        },
        'freeze_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'freeze.log'),
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        'pol_harvester': {
            'handlers': ['debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'freeze': {
            'handlers': ['freeze_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'datagrowth.command': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        }
    },
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/'
STATIC_ROOT = os.path.join(BASE_DIR, 'statics')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "..", "rateapp", "dist"),
]
# We're serving static files through Whitenoise
# See: http://whitenoise.evans.io/en/stable/index.html#
# If you doubt this decision then read the "infrequently asked question" section for details
WHITENOISE_INDEX_FILE = 'index.html'
if DEBUG:
    WHITENOISE_AUTOREFRESH = True
    WHITENOISE_USE_FINDERS = True

MEDIA_ROOT = os.path.join('..', 'media')

SESSION_COOKIE_PATH = '/admin/'


# Rest framework
# https://www.django-rest-framework.org/

REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}


# Celery
# https://docs.celeryproject.org/en/v4.1.0/

CELERY_BROKER_URL = 'redis://redis:6379/0' # 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = "django-db"
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERYD_TASK_TIME_LIMIT = 300  # 5 minutes for a single task


# Datagrowth
# https://github.com/fako/datascope/blob/master/datagrowth/settings.py

DATAGROWTH_DATA_DIR = os.path.join('..', 'data')
DATAGROWTH_REQUESTS_PROXIES = None
DATAGROWTH_REQUESTS_VERIFY = True
DATAGROWTH_DATETIME_FORMAT = "%Y%m%d%H%M%S%f"

DATAGROWTH_KALDI_BASE_PATH = '/home/surf/kaldi'
DATAGROWTH_KALDI_ASPIRE_BASE_PATH = '/home/surf/kaldi/egs/aspire/s5'
DATAGROWTH_KALDI_NL_BASE_PATH = '/home/surf/Kaldi_NL'

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GOOGLE_CX = os.environ.get("GOOGLE_CX")


# Elastic Search

ELASTIC_SEARCH_USERNAME = os.environ.get("ELASTIC_SEARCH_USERNAME", None)
ELASTIC_SEARCH_PASSWORD = os.environ.get("ELASTIC_SEARCH_PASSWORD", None)
ELASTIC_SEARCH_URL = os.environ.get("ELASTIC_SEARCH_URL", "https://surfpol.sda.surf-hosted.nl")
ELASTIC_SEARCH_HOST = os.environ.get("ELASTIC_SEARCH_HOST", "surfpol.sda.surf-hosted.nl")
ELASTIC_SEARCH_ANALYSERS = {
    'en': 'english',
    'nl': 'dutch'
}


# Project Open Leermaterialen

MIME_TYPE_TO_FILE_TYPE = {
    'unknown': 'unknown',
    'application/pdf': 'pdf',
    'application/x-pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'presentation',
    'application/vnd.openxmlformats-officedocument.presentationml.slideshow': 'presentation',
    'application/vnd.ms-powerpoint': 'presentation',
    'application/ppt': 'presentation',
    'application/msword': 'text',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'text',
    'application/rtf': 'text',
    'text/plain': 'text',
    'text/html': 'text',
    'application/vnd.ms-word': 'text',
    'application/vnd.ms-word.document.macroEnabled.12': 'text',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.template': 'text',
    'text/rtf':	'text',
    'application/xhtml+xml': 'text',
    'application/postscript': 'text',
    'application/vnd.ms-publisher':	'text',
    'text/xml': 'text',
    'application/vnd.oasis.opendocument.spreadsheet': 'spreadsheet',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'spreadsheet',
    'application/vnd.ms-excel': 'spreadsheet',
    'video/flv': 'video',
    'video/x-flv': 'video',
    'video/quicktime': 'video',
    'video': 'video',
    'video/x-msvideo': 'video',
    'video/mpeg': 'video',
    'application/x-mplayer2': 'video',
    'video/mp4': 'video',
    'video/x-ms-wmv': 'video',
    'video/x-ms-asf': 'video',
    'image': 'image',
    'image/bmp': 'image',
    'image/pjpeg': 'image',
    'image/png': 'image',
    'image/x-icon': 'image',
    'image/x-ms-bmp': 'image',
    'image/tiff': 'image',
    'image/jpg': 'image',
    'image/gif': 'image',
    'image/jpeg': 'image',
    'application/zip': 'archive',
    'application/x-tar': 'archive',
    'application/x-stuffit': 'archive',
    'application/x-rar-compressed': 'archive',
    'application/x-Wikiwijs-Arrangement': 'archive',
    'audio/mpeg': 'audio',
    'application/x-koan': 'audio',
    'application/vnd.koan':	'audio',
    'audio/midi': 'audio',
    'audio/x-wav': 'audio',
    'application/octet-stream': 'other',
    'application/x-yossymemo':	'digiboard',
    'application/Inspire': 'digiboard',
    'application/x-AS3PE': 'digiboard',
    'application/x-Inspire': 'digiboard',
    'application/x-smarttech-notebook': 'digiboard',
    'application/x-zip-compressed': 'digiboard',
    'application/x-ACTIVprimary3': 'digiboard',
    'application/x-ibooks+zip':	'ebook',
    'message/rfc822': 'message',
    'application/vnd.google-earth.kmz': 'googleearth',
    'application/x-java': 'app',
}

EXTENSION_TO_FILE_TYPE = {
    '.html': 'text',
    '.pdf': 'pdf',
    '.pptx': 'presentation',
    '.ppt': 'presentation',
    '.doc': 'text',
    '.docx': 'text',
    '.rtf': 'text',
    '.txt': 'text',
    '.xls': 'spreadsheet',
    '.xlsx': 'spreadsheet',
    '.png': 'image',
    '.jpeg': 'image',
    '.jpg': 'image',
    '.zip': 'zip',
}
