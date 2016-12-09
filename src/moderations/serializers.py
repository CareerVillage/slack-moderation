from rest_framework import serializers
from .models import ModerationAction


class ModerationSerializer(serializers.ModelSerializer):

    content_key = serializers.CharField()
    content = serializers.CharField()
    content_author_id = serializers.CharField()

    class Meta:
        model = ModerationAction
        fields = (
            'content_key',
            'content',
            'content_author_id',
            'action',
        )
