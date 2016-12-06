import json
import os
import requests

from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render

from social.apps.django_app.views import (
    auth as socialauth_auth,
    complete as socialauth_complete,
)
from social.backends.slack import SlackOAuth2
from social.exceptions import (
    AuthAlreadyAssociated, AuthCanceled
)

from moderation import settings


class SlackSdk(object):
    file_name = os.path.join(settings.APP_ROOT, '../tmp/slack.json')

    def __init__(self):
        self.data = {}
        with open(self.file_name, 'r') as f:
            contents = f.read()
            if contents != "":
                self.data = json.loads(contents)

    def create_message(self, channel_name, text='', attachments=[]):
        channel = self.data[channel_name]

        is_image = False
        if 'https://res.cloudinary.com/' in text:
            is_image = True

        return requests.get(
            url='https://slack.com/api/chat.postMessage',
            params={
                'token': channel['access_token'],
                'channel': channel['incoming_webhook']['channel_id'],
                'text': text,
                'attachments': json.dumps(attachments),
                'unfurl_links': False,
                'unfurl_media': is_image,
            }
        )

    def delete_message(self, channel_name, ts):
        channel = self.data[channel_name]
        return requests.get(
            url='https://slack.com/api/chat.delete',
            params={
                'token': channel['access_token'],
                'ts': ts,
                'channel': channel['incoming_webhook']['channel_id'],
            }
        )

    def update_message(self, channel_name, ts, text='', attachments=[]):
        channel = self.data[channel_name]
        return requests.get(
            url='https://slack.com/api/chat.update',
            params={
                'token': channel['access_token'],
                'ts': ts,
                'channel': channel['incoming_webhook']['channel_id'],
                'text': text,
                'attachments': json.dumps(attachments),
                'parse': 'none',
            }
        )


class SlackAuth(SlackOAuth2):
    name = 'slack'


def auth(request, *args, **kwargs):
    return socialauth_auth(request, *args, **kwargs)


def complete(request, *args, **kwargs):
    try:
        return socialauth_complete(request, *args, **kwargs)
    except AuthAlreadyAssociated:
        # The social account is already associated to another user
        return redirect('interactions')
    except AuthCanceled:
        # The user canceled the process
        return redirect('interactions')


def save_slack_integration(*args, **kwargs):
    data = kwargs.get('response')

    file_name = os.path.join(
        settings.APP_ROOT, '../tmp/slack.json'
    )

    with open(file_name, 'r') as f:
        contents = f.read()
        if contents != "":
            slack_app_json = json.loads(contents)
        else:
            slack_app_json = {}
        slack_app_json[data['incoming_webhook']['channel']] = data

        with open(file_name, 'w') as f:
            f.write(json.dumps(slack_app_json, indent=4))

    return reverse('interactions')
