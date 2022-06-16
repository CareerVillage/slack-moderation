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

    class Meta:
        indexes = [
            models.Index(fields=['content_author_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['status_reason']),
            models.Index(fields=['status_date']),
            models.Index(fields=['message_id']),
        ]


class ModerationAction(models.Model):
    """
    Keep history of back and forth between service and Slack.
    """
    moderation = models.ForeignKey(Moderation, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    action_author_id = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['moderation']),
            models.Index(fields=['action']),
            models.Index(fields=['action_author_id']),
            models.Index(fields=['created_at']),
        ]
