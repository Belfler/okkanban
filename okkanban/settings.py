import os
import pathlib

import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = pathlib.Path(__file__).parents[1]

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split()

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'core.apps.CoreConfig',
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

ROOT_URLCONF = 'okkanban.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'okkanban.wsgi.application'

ASGI_APPLICATION = 'okkanban.routing.application'

DATABASES = {'default': dj_database_url.config(env='DATABASE_URL')}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = False

USE_L10N = False

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'static'

AUTH_USER_MODEL = 'core.CustomUser'

LOGIN_URL = 'core:login'
LOGIN_REDIRECT_URL = 'core:summary'
LOGOUT_URL = 'core:logout'
LOGOUT_REDIRECT_URL = 'core:login'

DATE_FORMAT = 'd.m.y'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ['REDIS_URL']],
        },
    },
}

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CELERY_BROKER_URL = os.environ['REDIS_URL']
