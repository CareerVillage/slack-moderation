from __future__ import unicode_literals

from django.db import models


class ModerationManager(models.Manager):
    """
    Provide methods to reduce code in views.
    """

    def create_or_update(self, *args, **kwargs):
        """ Create or update Moderation entry
        """
        content_key = kwargs['content_key']
        content = kwargs['content']
        content_author_id = kwargs.get('content_author_id')
        action = kwargs['last_action']
        action_author_id = kwargs['last_action_author_id']
        moderation = self.filter(content_key=content_key).first()
        if moderation:
            moderation.last_action = action
            moderation.last_action_author_id
            moderation.save()
        else:
            moderation = self.create(content_key=content_key,
                                     content=content,
                                     content_author_id=content_author_id,
                                     last_action=action,
                                     last_action_author_id=action_author_id)

        return moderation

    def get_by_ts(self, ts):
        return self.filter(moderation_id=ts).first()


class Moderation(models.Model):
    """
    Record Moderation request from client service
    """
    content_key = models.TextField(unique=True)
    content = models.TextField()
    content_author_id = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_action = models.CharField(max_length=20)
    last_action_author_id = models.TextField()
    objects = ModerationManager()
    tls = models.TextField(blank=True, null=True)


class ModerationAction(models.Model):
    """
    Keep history of back and forth between service and Slack.
    """
    moderation = models.ForeignKey(Moderation)
    action = models.CharField(max_length=10)
    action_author_id = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
