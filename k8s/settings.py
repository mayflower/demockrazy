from demockrazy.settings import *
from os import getenv


def getenv_or_error(key):
    if (v := getenv(key)) is not None:
        return v
    raise Exception(f"Env variable {key} does not exist!")


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv_or_error('DEMOCKRAZY_DB_NAME'),
        'USER': getenv_or_error('DEMOCKRAZY_DB_USER'),
        'PASSWORD': getenv_or_error('DEMOCKRAZY_DB_PW'),
        'HOST': getenv_or_error('DEMOCKRAZY_DB_HOST'),
        'PORT': '5432',
    }
}

SECRET_KEY = getenv_or_error('DEMOCKRAZY_SECRET_KEY')
EMAIL_PORT = 587
EMAIL_HOST = getenv_or_error('DEMOCKRAZY_EMAIL_HOST')
EMAIL_HOST_PASSWORD = getenv_or_error('DEMOCKRAZY_EMAIL_PASSWORD')
VOTE_MAIL_FROM = getenv_or_error('DEMOCKRAZY_VOTE_MAIL_FROM')
VOTE_SEND_MAILS = True
ALLOWED_HOSTS = [getenv_or_error('DEMOCKRAZY_DOMAIN')]
