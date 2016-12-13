from rest_framework import serializers
from .models import ModerationAction


class ModerationSerializer(serializers.ModelSerializer):

    content_key = serializers.CharField(write_only=True)
    content = serializers.CharField(write_only=True)
    content_author_id = serializers.CharField(write_only=True)

    class Meta:
        model = ModerationAction
        fields = (
            'content_key',
            'content',
            'content_author_id',
            'action',
            'action_author_id',
        )
