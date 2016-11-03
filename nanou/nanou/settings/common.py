"""
Django settings for nanou project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import logging
import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

INTERNAL_IPS = (
    '127.0.0.1',
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social.apps.django_app.default',
    'nanou',
    'groups.apps.GroupsConfig',
    'neo.apps.NeoConfig',
    'socialusers.apps.SocialUsersConfig',
    'videos.apps.VideosConfig',
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

ROOT_URLCONF = 'nanou.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(os.path.join(BASE_DIR, 'nanou'), 'templates')],
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

WSGI_APPLICATION = 'nanou.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'landingpage'


AUTHENTICATION_BACKENDS = (
    'social.backends.google.GoogleOAuth2',
    'socialusers.backends.HpiOpenIdAuth',
    'django.contrib.auth.backends.ModelBackend',
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'nanou/static'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'npm.finders.NpmFinder',
]

NPM_ROOT_PATH = os.path.dirname(BASE_DIR)

NPM_FILE_PATTERNS = {
    'semantic-ui': [
        'dist/semantic.min.js',
        'dist/semantic.min.css',
        'dist/themes/default/assets/fonts/*',
    ],
    'jquery': [
        'dist/jquery.min.js',
        'dist/jquery.min-map',
    ],
}


# According to http://12factor.net/logs we always log to stdout/stderr and do not manage log files.
# Production log files are managed by the production execution environment, never Django itself.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'nanou': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


# Example neo4j config
# Configure your instance in local_settings.py
NEO_DATABASE = {
    'secure': False,
    'host': 'localhost',
    'http_port': 7474,
    'https_port': 7473,
    'bolt_port': 7687,
    'user': 'neo4j',
    'password': 'neo4j',
}

TEST_NEO_DATABASE = {
    'bolt': False,
    'secure': False,
    'host': 'localhost',
    'http_port': 7475,
    'user': 'neo4j',
    'password': 'neo4j',
}


###########################################
# Social Auth                             #
###########################################
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_LOGIN_URL = 'sociallogin:login'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'sociallogin:logged_in'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''  # configure google oauth2 in local_settings.py
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''


TESTING = any(arg.endswith('test') for arg in sys.argv)

# speed up tests
if TESTING:
    DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3'}  # use sqlite
    logging.disable(logging.CRITICAL)

INSECURE = '--insecure' in sys.argv
