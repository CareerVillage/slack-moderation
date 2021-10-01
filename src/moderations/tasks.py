from __future__ import absolute_import
import requests
from .models import Moderation


def async_get_request(url, params):
    return requests.get(url, params)


def post_moderation_async(moderation_id, data):
    from .slack import SlackSdk
    slack = SlackSdk()
    response_data = slack.post_moderation(
        text=data['content'])
    message_id = response_data.get('ts')
    moderation = Moderation.objects.get(id=moderation_id)
    moderation.message_id = message_id
    moderation.save()
