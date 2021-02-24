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

SOCIAL_AUTH_SLACK_KEY = '105721919958.1737964162128'
SOCIAL_AUTH_SLACK_SECRET = '40d59eca259cc11ba4ddd40f10033f79'
SOCIAL_AUTH_SLACK_SCOPE = ['incoming-webhook', 'chat:write:user', 'chat:write:bot']
