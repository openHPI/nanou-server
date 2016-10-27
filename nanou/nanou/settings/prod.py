from .common import *  # noqa


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

SECRET_KEY = 'uxv*l4)co)wm1*7o@if@r3p@+-=u6&)@78d#-4+93&03vg*!ze'

DEBUG = False

ALLOWED_HOSTS = ['*']


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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


LOGGING['loggers']['nanou']['level'] = 'INFO'  # noqa


# Create a local_settings.py to override settings with sensible values
# that shall not be checked in to the repository

try:
    from .local_settings import *  # noqa
except ImportError:
    pass
