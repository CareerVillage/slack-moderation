import os

import environ
import envkey  # noqa
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

env = environ.Env()


def rel(*x):
    """Get the full root for the specified path relative to this file."""
    return os.path.join(APP_ROOT, *x)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")

ENVIRONMENT = env.str("ENVIRONMENT", "DEVELOPMENT")

DEBUG = False

SECRET_KEY = env.str("SECRET_KEY")

ec2_ip_address = env.str("EC2_IP", "")
ec2_url_address = env.str("EC2_URL", "")

if ENVIRONMENT == "DEVELOPMENT":
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = ["slack-moderation.com", ec2_ip_address, ec2_url_address]

REST_FRAMEWORK = {"DEFAULT_AUTHENTICATION_CLASSES": []}

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "moderations",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "moderation.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            rel("apps/moderations/templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "moderation.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation." "MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation." "CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation." "NumericPasswordValidator",
    },
]

# Celery
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", "")

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files
STATIC_ROOT = rel("assets/")
STATIC_URL = "/static/"
STATIC_APP_ROOT = rel("static/")

STATICFILES_DIRS = (STATIC_APP_ROOT,)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

AUTHENTICATION_BACKENDS = ()

RAISE_EXCEPTIONS = True

LOGIN_REDIRECT_URL = "/"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": None,
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("POSTGRES_DB"),
        "USER": env.str("POSTGRES_USER"),
        "PASSWORD": env.str("POSTGRES_PASSWORD"),
        "HOST": env.str("POSTGRES_HOST"),
        "PORT": env.str("POSTGRES_PORT"),
    }
}

SLACK_BOT_OAUTH_TOKEN = env.str("SLACK_BOT_OAUTH_TOKEN")
SLACK_SIGNING_SECRET = env.str("SLACK_SIGNING_SECRET")

ENABLE_SENTRY = ENVIRONMENT != "DEVELOPMENT"
if ENABLE_SENTRY:
    SENTRY_DSN = env.str("SENTRY_DSN", "")
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
    )

if ENVIRONMENT == "DEVELOPMENT":
    CV_BASE_URL = (
        "http://192.168.1.7:8080"  # Put your router local ip + :8000 port in here
    )
else:
    CV_BASE_URL = env.str("CV_BASE_URL")

# API key used to authenticate request coming/going from/to Q&A
CV_MODERATION_API_KEY = env.str("CV_MODERATION_API_KEY")
