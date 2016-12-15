from __future__ import unicode_literals

from django.db import models


class ModerationManager(models.Manager):
    """
    Provide methods to reduce code in views.
    """

    def get_by_message_id(self, message_id):
        return self.filter(message_id=message_id).first()


class Moderation(models.Model):
    """
    Record Moderation request from client service
    """
    content_key = models.TextField()
    content = models.TextField()
    content_author_id = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    status_reason = models.CharField(max_length=50)
    status_date = models.DateTimeField(auto_now=True)
    message_id = models.TextField(blank=True, null=True)

    objects = ModerationManager()


class ModerationAction(models.Model):
    """
    Keep history of back and forth between service and Slack.
    """
    moderation = models.ForeignKey(Moderation)
    action = models.CharField(max_length=50)
    action_author_id = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
