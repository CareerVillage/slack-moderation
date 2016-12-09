from datetime import datetime
import json
import requests
from django.http import HttpResponse
from accounts.models import AuthToken


class SlackSdk(object):

    @staticmethod
    def get_channel_data(channel):
        auth_token_object = AuthToken.objects.filter(
            service_name='slack', service_entity_auth_name=channel
        ).first()
        channel_id = auth_token_object.service_entity_auth_id
        token = auth_token_object.service_auth_token

        return token, channel_id

    @staticmethod
    def post_moderation(text):

        attachments = [
            {
                'fallback': "Moderator actions",
                'callback_id': 'mod-inbox',
                'attachment_type': 'default',
                'actions': [
                    {
                        'name': 'approve',
                        'text': "Approve",
                        'type': 'button',
                        'value': 'approve',
                        'style': 'primary'
                    },
                    {
                        'name': 'reject',
                        'text': "Reject",
                        'type': 'button',
                        'value': 'reject'
                    }
                ]
            }
        ]

        token, channel_id = SlackSdk.get_channel_data('#mod-inbox')
        return SlackSdk.create_message(token, channel_id, text, attachments)

    @staticmethod
    def create_message(access_token, channel_id,
                       text='', attachments=[]):

        is_image = False
        if 'https://res.cloudinary.com/' in text:
            is_image = True

        return requests.get(
            url='https://slack.com/api/chat.postMessage',
            params={
                'token': access_token,
                'channel': channel_id,
                'text': text,
                'attachments': json.dumps(attachments),
                'unfurl_links': False,
                'unfurl_media': is_image,
            }
        )

    @staticmethod
    def delete_message(access_token, channel_id, ts):
        return requests.get(
            url='https://slack.com/api/chat.delete',
            params={
                'token': access_token,
                'ts': ts,
                'channel': channel_id,
            }
        )

    @staticmethod
    def update_message(access_token, channel_id, ts,
                       text='', attachments=[]):

        return requests.get(
            url='https://slack.com/api/chat.update',
            params={
                'token': access_token,
                'ts': ts,
                'channel': channel_id,
                'text': text,
                'attachments': json.dumps(attachments),
                'parse': 'none',
            }
        )


def mod_inbox_approved(data):

    original_message = data.get('original_message')
    text = original_message.get('text')
    approved_by = data.get('user').get('name')
    approved_time = float(data.get('action_ts').split('.')[0])
    approved_time = datetime.utcfromtimestamp(approved_time)
    approved_time = approved_time.strftime('%Y-%m-%d %I:%M%p')

    attachments = [
        {
            "fallback": "Please moderate this.",
            "text": ":white_check_mark: _Approved by @%s %s UTC_" %
                    (approved_by, approved_time),
            "callback_id": "mod-approved",
            "attachment_type": "default",
            "mrkdwn_in": [
                "text"
            ]
        }
    ]

    token, channel_id = SlackSdk.get_channel_data('#mod-approved')
    print token
    print channel_id
    SlackSdk.create_message(token, channel_id, text, attachments)

    ts = data.get('message_ts')
    print token
    print channel_id
    token, channel_id = SlackSdk.get_channel_data('#mod-inbox')
    SlackSdk.delete_message(token, channel_id, ts)

    return HttpResponse('')


def mod_inbox_reject(data):
    original_message = data.get('original_message')
    text = original_message.get('text')

    attachments = [
        {
            "fallback": "Moderator actions",
            "text": "_Reject: Select a reason_",
            "callback_id": "mod-inbox",
            "attachment_type": "default",
            "mrkdwn_in": [
                "text"
            ],
            "actions": [
                {
                    "name": "Off topic",
                    "text": "Off topic",
                    "type": "button",
                    "value": "off_topic",
                    "style": "danger"
                },
                {
                    "name": "Inappropriate",
                    "text": "Inappropriate",
                    "type": "button",
                    "value": "inappropriate",
                    "style": "danger"
                },
                {
                    "name": "Contact info",
                    "text": "Contact info",
                    "type": "button",
                    "value": "contact_info",
                    "style": "danger"
                },
                {
                    "name": "Other",
                    "text": "Other",
                    "type": "button",
                    "value": "other",
                    "style": "danger"
                },
                {
                    "name": "Undo",
                    "text": "Undo",
                    "type": "button",
                    "value": "undo"
                }
            ]
        }
    ]

    token, channel_id = SlackSdk.get_channel_data('#mod-inbox')
    ts = data.get('message_ts')
    SlackSdk.update_message(token, channel_id, ts,
                            text=text, attachments=attachments)

    return HttpResponse('')


def mod_inbox_reject_undo(data):
    original_message = data.get('original_message')
    text = original_message.get('text')

    attachments = [
        {
            "fallback": "Moderator actions",
            "callback_id": "mod-inbox",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "approve",
                    "text": "Approve",
                    "type": "button",
                    "value": "approve",
                    "style": "primary"
                },
                {
                    "name": "reject",
                    "text": "Reject",
                    "type": "button",
                    "value": "reject"
                }
            ]
        }
    ]

    token, channel_id = SlackSdk.get_channel_data('#mod-inbox')
    ts = data.get('message_ts')
    SlackSdk.update_message(token, channel_id,
                            ts, text=text, attachments=attachments)

    return HttpResponse('')


def mod_inbox_reject_reason(data):
    original_message = data.get('original_message')
    text = original_message.get('text')
    rejected_by = data.get('user').get('name')
    rejected_time = float(data.get('action_ts').split('.')[0])
    rejected_time = datetime.utcfromtimestamp(rejected_time)
    rejected_time = rejected_time.strftime('%Y-%m-%d %I:%M%p')
    rejected_reason = data.get('actions')[0]['name']

    attachments = [
        {
            "fallback": "Moderator actions",
            "text": "_%s UTC: @%s rejected this with the reason: \"%s\"_" %
                    (rejected_time, rejected_by, rejected_reason),
            "callback_id": "mod-flagged",
            "attachment_type": "default",
            "mrkdwn_in": [
                "text"
            ],
            "actions": [
                {
                    "name": "Resolve",
                    "text": "Mark resolved",
                    "type": "button",
                    "value": "resolve",
                    "style": "primary"
                }
            ]
        }
    ]

    token, channel_id = SlackSdk.get_channel_data('#mod-flagged')

    SlackSdk.create_message(token, channel_id,
                            text=text, attachments=attachments)

    token, channel_id = SlackSdk.get_channel_data('#mod-inbox')
    ts = data.get('message_ts')
    SlackSdk.delete_message(token, channel_id, ts)

    return HttpResponse('')


def mod_inbox(data):
    actions = data.get('actions')[0]
    action = actions.get('value')

    if action == 'approve':
        return mod_inbox_approved(data)

    elif action == 'reject':
        return mod_inbox_reject(data)

    elif action == 'undo':
        return mod_inbox_reject_undo(data)

    elif (action == 'off_topic') or (action == 'inappropriate') \
            or (action == 'contact_info') or (action == 'other'):
        return mod_inbox_reject_reason(data)


def mod_flagged_resolve(data):
    original_message = data.get('original_message')
    text = original_message.get('text')
    resolved_by = data.get('user').get('name')
    resolved_time = float(data.get('action_ts').split('.')[0])
    resolved_time = datetime.utcfromtimestamp(resolved_time)
    resolved_time = resolved_time.strftime('%Y-%m-%d %I:%M%p')
    rejected_reason = original_message.get('attachments')[0]['text']

    attachments = [
        {
            "fallback": "Please moderate this.",
            "text": "%s\n_%s UTC: @%s marked this \"Resolved\"_" %
                    (rejected_reason, resolved_time, resolved_by),
            "callback_id": "mod-resolved",
            "attachment_type": "default",
            "mrkdwn_in": [
                "text"
            ]
        }
    ]

    token, channel_id = SlackSdk.get_channel_data('#mod-resolved')
    SlackSdk.create_message(token, channel_id, text=text,
                            attachments=attachments)

    token, channel_id = SlackSdk.get_channel_data('#mod-flagged')
    ts = data.get('message_ts')
    SlackSdk.delete_message(token, channel_id, ts)

    return HttpResponse('')


def mod_flagged(data):
    actions = data.get('actions')[0]
    action = actions.get('value')

    if action == 'resolve':
        return mod_flagged_resolve(data)


def moderate(data):
    payload = data.get('payload')

    if payload:
        data = json.loads(payload)
        callback_id = data.get('callback_id')

        if callback_id == 'mod-inbox':
            return mod_inbox(data)

        elif callback_id == 'mod-flagged':
            return mod_flagged(data)

        return HttpResponse(json.dumps(data, indent=4))

    return HttpResponse('Hello world.')
