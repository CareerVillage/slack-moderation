import os
import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')


def rel(*x):
    """ Get the full root for the specified path relative to this file.
    """
    return os.path.join(APP_ROOT, *x)


ALLOWED_HOSTS = ['*']

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': []
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'social_django',
    'accounts',
    'moderations',
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

ROOT_URLCONF = 'moderation.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            rel('apps/moderations/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'moderation.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files
STATIC_ROOT = rel('assets/')
STATIC_URL = '/static/'
STATIC_APP_ROOT = rel('static/')

STATICFILES_DIRS = (
    STATIC_APP_ROOT,
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTHENTICATION_BACKENDS = (
    'social_core.backends.slack.SlackOAuth2',
)


SOCIAL_AUTH_JSONFIELD_ENABLED = True
SLACK_SOCIAL_AUTH_RAISE_EXCEPTIONS = True
SOCIAL_AUTH_RAISE_EXCEPTIONS = True
RAISE_EXCEPTIONS = True


SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'accounts.views.social_complete',
)

LOGIN_REDIRECT_URL = '/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': None,
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

if os.environ.get('ENVIRONMENT', 'Development') == 'Production':
    import envkey

    env = environ.Env()

    DEBUG = False
    TEMPLATE_DEBUG = DEBUG

    ENABLE_SENTRY = True

    SECRET_KEY = env.str('SECRET_KEY')

    ec2_ip_address = env.str('EC2_IP')
    ec2_url_address = env.str('EC2_URL')
    ALLOWED_HOSTS = ['slack-moderation.com', ec2_ip_address, ec2_url_address]

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env.str('POSTGRES_DB'),
            'USER': env.str('POSTGRES_USER'),
            'PASSWORD': env.str('POSTGRES_PASSWORD'),
            'HOST': env.str('POSTGRES_HOST'),
            'PORT': '5432',
        }
    }

    SOCIAL_AUTH_SLACK_KEY = env.str('SOCIAL_AUTH_SLACK_KEY')
    SOCIAL_AUTH_SLACK_SECRET = env.str('SOCIAL_AUTH_SLACK_SECRET')
    SOCIAL_AUTH_SLACK_SCOPE = ['incoming-webhook', 'chat:write:user', 'chat:write:bot',
                               'channels:history', 'groups:history', 'mpim:history', 'im:history']

    SENTRY_DSN = env.str('SENTRY_DSN', '')
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )

else:
    from .local import *
