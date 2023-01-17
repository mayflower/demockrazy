from demockrazy.settings import *
from os import getenv


def getenv_or_error(key):
    if v := getenv(key) is not None:
        return v
    raise Exception(f"Env variable {key} does not exist!")


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'NAME': getenv_or_error('DEMOCKRAZY_DB_NAME'),
            'USER': getenv_or_error('DEMOCKRAZY_DB_USER'),
            'PASSWORD': getenv_or_error('DEMOCKRAZY_DB_PW'),
            'HOST': getenv_or_error('DEMOCKRAZY_DB_HOST'),
            'PORT': '5432',
        }
    }
}

SECRET_KEY = getenv_or_error('DEMOCKRAZY_SECRET_KEY')
EMAIL_PORT = getenv_or_error('DEMOCKRAZY_EMAIL_PORT')
EMAIL_HOST = getenv_or_error('DEMOCKRAZY_EMAIL_HOST')
VOTE_MAIL_FROM = getenv_or_error('DEMOCKRAZY_VOTE_MAIL_FROM')
VOTE_SEND_MAILS = True
