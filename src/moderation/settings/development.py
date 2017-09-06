DEBUG = False
ENABLE_SENTRY = False


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'moderation',
        'USER': 'moderation',
        'PASSWORD': 'moderation',
        'HOST': 'localhost',
        'PORT': '',
    }
}

SOCIAL_AUTH_SLACK_KEY = '105721919958.106208312007'
SOCIAL_AUTH_SLACK_SECRET = 'f56bc4b6ed1cad650426a85e7e7826b6'
SOCIAL_AUTH_SLACK_SCOPE = ['incoming-webhook', 'chat:write:user', 'chat:write:bot']
