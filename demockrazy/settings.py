"""
Django settings for demockrazy project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%cs8fdyvv=@dbe7g^ltxt!=!c(033*tm$br3x%c%u@1%szg8#_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [ ]


# Application definition

INSTALLED_APPS = [
    'vote.apps.VoteConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'demockrazy.urls'

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

WSGI_APPLICATION = 'demockrazy.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
ATOMIC_REQUESTS = True


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

EMAIL_HOST = ""
EMAIL_PORT = 25
#EMAIL_HOST_USER = "derp"
#EMAIL_HOST_PASSWORD = "derp"
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

VOTE_MAIL_FROM = "WahlLeitung@mayflower.de"
VOTE_BASE_URL = 'http://127.0.0.1:8000'
VOTE_MAIL_SUBJECT = "demockrazy: Eine neue Abstimmung ist verfügbar"
VOTE_MAIL_TEXT = '''
Hallo,

Jemand hat eine Abstimmung auf %(vote_base_url)s erstellt.
Du wurdest eingeladen an dieser Abstimmung teilzunehmen.

Dies ist dir über folgenden Link möglich:
%(poll_url_with_token)s

Nach Abgabe deiner Stimme wird der Token aus der Datenbank gelöscht.
Dadurch gibt es keine Korrelation zwischen Token (Teilnehmer) und abgegebener Stimme.

Die Umfrage wird automatisch beendet, sobald alle Tokens verbraucht wurden. Nach Beendigung sind die Umfrageergebnisse sichtbar.
Der Ersteller der Umfrage hat die möglichkeit diese vorzeitig zu beenden.

XoXoXo
Die Wahlleitung

'''

VOTE_SEND_MAILS = False

try:
  from .local_settings import *
except ImportError:
  print("No local settings found..")
