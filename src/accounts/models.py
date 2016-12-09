from __future__ import unicode_literals

from django.db import models

# Create your models here.
class AuthToken(models.Model):
    """
    Store auth tokens returned by the moderation backend service (Slack)
    """

    service_name = models.TextField()
    service_entity_auth_name = models.TextField()
    service_entity_auth_id = models.TextField()
    service_auth_token = models.TextField()
    username = models.CharField(max_length=50)
