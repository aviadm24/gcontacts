"""
Django settings for gcontacts project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import dj_database_url
import socket
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_lkurf#cy@r^+lso44bf!-((_oau!mx@=)ri*q3tgo38y2%04%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'danielavida.herokuapp.com', 'www.pythoninhebrew.com', 'h.lavida.co.il']


# Application definition

INSTALLED_APPS = [
    'main',
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.file'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'gcontacts.urls'

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

WSGI_APPLICATION = 'gcontacts.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

ipaddress = socket.gethostbyname(socket.gethostname())
print('ip_address:', ipaddress)
if not ipaddress.startswith('172'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {}
    DATABASES['default'] = dj_database_url.config()


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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)
# very important for aws! - https://stackoverflow.com/questions/42462880/how-to-serve-static-files-to-aws-when-deploying-django-app-python-manage-py-co
#STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'aviadm32@gmail.com'
EMAIL_HOST_PASSWORD = 'aviadpython'

ipaddress = socket.gethostbyname(socket.gethostname())
# print('ip_address:', ipaddress)
if not ipaddress.startswith('172'):
    FN_AUTH_REDIRECT_URI = "http://localhost:8000/google/auth"
    FN_BASE_URI = "http://localhost:8000"
    FN_CLIENT_ID = "37866652038-qh3b1ni3e1b5ad8n3beds83s7e1jt1fj.apps.googleusercontent.com"
    FN_CLIENT_SECRET = "kds92jr8z4Esb92VImChdTih"
    AUTHORIZATION_SCOPE = 'openid email profile https://www.googleapis.com/auth/contacts https://www.googleapis.com/auth/drive.file'
    ACTION_URL = "http://localhost:8000/action_check"
    # ACTION_URL = 'https://api.lavida.co.il:444/webhooks/google/jiswy7t5i9hdeghe4dehujkgfu839i9idej37gaa2hdia3u8'
    SAFE_IP = '127.0.0.1'
else:
    FN_AUTH_REDIRECT_URI = "https://www.pythoninhebrew.com/google/auth"
    FN_BASE_URI = "https://www.pythoninhebrew.com"
    FN_CLIENT_ID = "992071002901-0nh1snrfe60qep8crvegt833oksqlhvg.apps.googleusercontent.com"
    FN_CLIENT_SECRET = "8wKO2wWzfQ-j_wq0csr3_BdB"
    AUTHORIZATION_SCOPE = 'openid email profile https://www.googleapis.com/auth/contacts'
    # ACTION_URL = 'https://aviad2.herokuapp.com/action_check'
    ACTION_URL = 'https://api.lavida.co.il:444/google/jiswy7t5i9hdeghe4dehujkgfu839i9idej37gaa2hdia3u8'
    SAFE_IP = ['192.116.50.2', '213.151.44.75', '192.168.1.15', '5.28.139.232']