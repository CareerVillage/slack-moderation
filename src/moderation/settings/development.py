DEBUG = False
ENABLE_SENTRY = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'moderation',
        'USER': 'moderation',
        'PASSWORD': 'moderation',
        'HOST': 'postgres',
        'PORT': '5433',
    }
}

SOCIAL_AUTH_SLACK_KEY = ''  # Do not commit secrets into version control (plus: this is public repo!)
SOCIAL_AUTH_SLACK_SECRET = ''  # Do not commit secrets into version control (plus: this is public repo!)
SOCIAL_AUTH_SLACK_SCOPE = ['incoming-webhook', 'chat:write:user', 'chat:write:bot',
                           'channels:history', 'groups:history', 'mpim:history', 'im:history']
