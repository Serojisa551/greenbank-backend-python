import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-v5i87d9nd(+8ku%f!2@82^7+gy4y4h612h^ns(314mrdfkgz(^"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cards",
    "authentication",
    "accounts",
    "currency",
    "transaction",
    "users",
    
    "drf_yasg",
    "corsheaders",
    "channels",
    "ratelimit",
]

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"},
    },
}

ASGI_APPLICATION = 'greenBank.asgi.application'

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_ratelimit.middleware.RatelimitMiddleware",
    "authentication.middleware.BearerTokenAuthenticationMiddleware",
    "authentication.middleware.UsersAuthenticationMiddleware",
    "transaction.middleware.TransactionMiddleware",
    "users.middleware.UsersMiddleware",
    "accounts.middleware.AccountMiddelware",
]

RATELIMIT_VIEW = 'authentication.utils.rate_limit_exceeded_handler'
ROOT_URLCONF = "greenBank.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "greenBank.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "djongo",
        "NAME": "greenBank",  # Choose your preferred database name
        "CLIENT": {
            "host": "mongodb://127.0.0.1:27017",
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 10

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

