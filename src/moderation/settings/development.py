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

SOCIAL_AUTH_SLACK_KEY = '' # Do not commit secrets into version control (plus: this is public repo!)
SOCIAL_AUTH_SLACK_SECRET = '' # Do not commit secrets into version control (plus: this is public repo!)
SOCIAL_AUTH_SLACK_SCOPE = ['incoming-webhook', 'chat:write:user', 'chat:write:bot']
