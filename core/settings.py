# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from decouple import config
from unipath import Path
import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(env_file=".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="S#perS3crEt_1122")

# TODO
# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = config("DEBUG", default=True, cast=bool)
DEBUG = env("DEBUG")

# load production server from .env
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    'dynweb.duckdns.org',
    config("SERVER", default="127.0.0.1"),
    ".herokuapp.com",
]

# hashed for password
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]

# set custom user
AUTH_USER_MODEL = "users.CustomUser"

# authentication backends
AUTHENTICATION_BACKENDS = [
    # 'django.contrib.auth.backends.ModelBackend',
    "apps.users.backends.SettingsBackend",
]

# Application definition

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django_extensions",
    "django_starfield",
    "mathfilters",
    "apps.ads",
    "apps.users",
    "apps.geolocation",
    "sweetify"
]

# security materials
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"
LOGIN_REDIRECT_URL = "home"  # Route defined in ads/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in ads/urls.py
TEMPLATE_DIR = os.path.join(CORE_DIR, "apps/templates")  # ROOT dir for templates

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("POSTGRES_DBNAME"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASS"),
        "HOST": env("PG_HOST"),
        "PORT": env("PG_PORT"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tehran"

USE_I18N = True

USE_L10N = True

USE_TZ = True

#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(CORE_DIR, "core/staticfiles")
STATIC_URL = "/static/"

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (os.path.join(CORE_DIR, "apps/static"),)
SWEETIFY_SWEETALERT_LIBRARY = 'sweetalert2'

#############################################################
#############################################################

# if os.name == "nt":
#     VENV_BASE = "C:\\Users\\ARIAN\\AppData\\Local\\Programs\\Python\\Python39"
#     os.environ["PATH"] = (
#         os.path.join(VENV_BASE, "Lib\\site-packages\\osgeo") + ";" + os.environ["PATH"]
#     )
#     print(os.environ["PATH"])
#     print("-------")
#     os.environ["PROJ_LIB"] = (
#         os.path.join(VENV_BASE, "Lib\\site-packages\\osgeo\\data\\proj")
#         + ";"
#         + os.environ["PATH"]
#     )
#     print(os.environ["PROJ_LIB"])
