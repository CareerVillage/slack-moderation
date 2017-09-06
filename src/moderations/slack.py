# -*- coding: utf-8 -*-

from datetime import datetime
import json
import re
import requests
from django.http import HttpResponse
from accounts.models import AuthToken
from moderations.models import Moderation, ModerationAction
from moderations.utils import timedelta_to_str


class SlackSdk(object):

    @staticmethod
    def get_channel_data(channel):
        auth_token_object = AuthToken.objects.filter(
            service_name='slack', service_entity_auth_name=channel
        ).first()
        if auth_token_object:
            channel_id = auth_token_object.service_entity_auth_id
            token = auth_token_object.service_auth_token

            return token, channel_id
        else:
            return None, None

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
        if channel_id:
            response = SlackSdk.create_message(token,
                                               channel_id, text, attachments)

            return response.json()
        else:
            data = {
                'success': False,
                'message': "{} is not a valid channel or "
                           "was not previously authorized".format(channel_id)
            }
            return data

    @staticmethod
    def post_leaderboard(leaderboard):
        """
        leaderboard = [
            {'@jared': 12,345},
        ]
        """

        def render_board(leaderboard, title):
            text = '┌----------------------┬----------------------┐\n'
            text += '│ {0: <20} | {1: <20} │\n'.format('Mod', title)

            sorted_leaderboard = sorted(leaderboard.items(),
                                        key=lambda x: x[1],
                                        reverse=True)
            for k, v in sorted_leaderboard:
                if k:
                    text += '├----------------------┼----------------------┤\n'
                    text += '│ {0: <20} │ {1: <20} │\n'.format(k, v)

            text += '└----------------------┴----------------------┘\n'
            return text


        def avg(a, b):
            if b > 0.0:
                return a/float(b) * 100.0
            else:
                return 0

        text = (
            "LEADERBOARD as of {date}\n"
            "```\n"
            "{all_time}\n"
            "{seven_days}\n"
            "```\n"
        )
        text = text.format(
            date=datetime.utcnow(),
            all_time=render_board(leaderboard['all_time'], 'All Time'),
            seven_days=render_board(leaderboard['seven_days'], 'Last 7 Days')
        )

        text += 'MOD TEAM SPEED REPORT AS OF {} UTC\n'.format(datetime.utcnow())
        text += '```\n'
        text += 'Average time to first mod review (all-time): %s over %i pieces of content\n' \
            % (timedelta_to_str(leaderboard['avg']['all_time']['review'][0]),
               leaderboard['avg']['all_time']['review'][1])

        text += 'Average time to first mod review (last 7 days): %s over %i pieces of content\n' \
            % (timedelta_to_str(leaderboard['avg']['seven_days']['review'][0]),
               leaderboard['avg']['seven_days']['review'][1])

        text += 'Average time to first mod resolution (all-time): %s over %i pieces of content\n' \
            % (timedelta_to_str(leaderboard['avg']['all_time']['resolution'][0]),
               leaderboard['avg']['all_time']['resolution'][1])

        text += 'Average time to first mod resolution (last 7 days): %s over %i pieces of content\n' \
            % (timedelta_to_str(leaderboard['avg']['seven_days']['resolution'][0]),
               leaderboard['avg']['seven_days']['resolution'][1])
        text += '```\n'

        text += 'CONTENT QUALITY REPORT AS OF {} UTC\n'.format(datetime.utcnow())
        counts = leaderboard['counts']
        text += '```\n'
        text += 'Past 7 days content: %i\n' \
            % counts['total']

        text += 'Past 7 days flagged by mods: %i (%.2f%%)\n' \
            % (counts['total_flagged'],
               avg(counts['total_flagged'], counts['total']))

        text += 'Reason: Off topic: %i (%.2f%% of flags)\n' \
            % (counts['off_topic'],
               avg(counts['off_topic'], counts['total_flagged']))

        text += 'Reason: Inappropriate: %i (%.2f%% of flags)\n' \
            % (counts['inappropriate'],
               avg(counts['inappropriate'], counts['total_flagged']))

        text += 'Reason: Contact info: %i (%.2f%% of flags)\n' \
            % (counts['contact_info'],
               avg(counts['contact_info'], counts['total_flagged']))

        text += 'Reason: Other: %i (%.2f%% of flags)\n' \
            % (counts['other'],
               avg(counts['other'], counts['total_flagged']))
        text += '```\n'

        token, channel_id = SlackSdk.get_channel_data('#mod-leaderboard')
        return SlackSdk.create_message(token, channel_id,
                                       text, [], in_channel=True)

    @staticmethod
    def create_message(access_token, channel_id,
                       text='', attachments=[], in_channel=False):

        is_image = False
        if 'https://res.cloudinary.com/' in text:
            is_image = True

        if len(text) >= 3500:
            search_text = re.findall(
                '^(.* posted the) <(https://.*)\|(.*)>.*:\n',
                text
            )
            if search_text:
                new_content_text = search_text[0][0]
                link = search_text[0][1]
                new_content_type = search_text[0][2]
                text = '%s %s. WARNING: this content cannot be displayed, ' \
                       'please read the complete content <%s|HERE>' \
                       % (new_content_text, new_content_type, link)

        params = {
            'token': access_token,
            'channel': channel_id,
            'text': text,
            'attachments': json.dumps(attachments),
            'unfurl_links': False,
            'unfurl_media': is_image,
        }
        if in_channel:
            params['response_type'] = 'in_channel'

        return requests.get(
            url='https://slack.com/api/chat.postMessage',
            params=params
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


def mod_inbox_approved(data, moderation):

    original_message = data.get('original_message')
    text = original_message.get('text')
    approved_by = data.get('user').get('name')
    approved_time = float(data.get('action_ts').split('.')[0])
    approved_time = datetime.utcfromtimestamp(approved_time)
    approved_time = approved_time.strftime('%Y-%m-%d %I:%M%p')
    ts = data.get('message_ts')

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
    response = SlackSdk.create_message(token, channel_id, text, attachments)
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            token, channel_id = SlackSdk.get_channel_data('#mod-inbox')
            save_moderation_action(moderation, approved_by, channel_id,
                                   'approve', data.get('ts'))
            reponse = SlackSdk.delete_message(token, channel_id, ts)

    return HttpResponse('')


def mod_inbox_reject(data, moderation):

    original_message = data.get('original_message')
    text = original_message.get('text')
    ts = data.get('message_ts')

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
    response = SlackSdk.update_message(token, channel_id, ts,
                                       text=text, attachments=attachments)

    data = response.json()

    return HttpResponse('')


def mod_inbox_reject_undo(data):
    original_message = data.get('original_message')
    text = original_message.get('text')
    ts = data.get('message_ts')

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
    SlackSdk.update_message(token, channel_id,
                            ts, text=text, attachments=attachments)

    return HttpResponse('')


def mod_inbox_reject_reason(data, moderation):
    original_message = data.get('original_message')
    text = original_message.get('text')
    rejected_by = data.get('user').get('name')
    rejected_time = float(data.get('action_ts').split('.')[0])
    rejected_time = datetime.utcfromtimestamp(rejected_time)
    rejected_time = rejected_time.strftime('%Y-%m-%d %I:%M%p')
    rejected_reason = data.get('actions')[0]['value']
    ts = data.get('message_ts')

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

    response = SlackSdk.create_message(token, channel_id,
                                       text=text, attachments=attachments)

    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):

            token, channel_id = SlackSdk.get_channel_data('#mod-inbox')

            save_moderation_action(moderation, rejected_by,
                                   channel_id, rejected_reason, data.get('ts'))

            SlackSdk.delete_message(token, channel_id, ts)

    return HttpResponse('')


def mod_inbox(data, action, moderation):

    if action == 'approve':
        return mod_inbox_approved(data, moderation)

    elif action == 'reject':
        return mod_inbox_reject(data, moderation)

    elif action == 'undo':
        return mod_inbox_reject_undo(data)

    elif (action == 'off_topic') or (action == 'inappropriate') \
            or (action == 'contact_info') or (action == 'other'):
        return mod_inbox_reject_reason(data, moderation)


def mod_flagged_resolve(data, moderation):
    original_message = data.get('original_message')
    text = original_message.get('text')
    resolved_by = data.get('user').get('name')
    resolved_time = float(data.get('action_ts').split('.')[0])
    resolved_time = datetime.utcfromtimestamp(resolved_time)
    resolved_time = resolved_time.strftime('%Y-%m-%d %I:%M%p')
    rejected_reason = original_message.get('attachments')[0]['text']
    message_ts = data.get('message_ts')

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
    response = SlackSdk.create_message(token, channel_id, text=text,
                                       attachments=attachments)

    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):

            token, channel_id = SlackSdk.get_channel_data('#mod-flagged')
            ts = data.get('ts')

            save_moderation_action(moderation, resolved_by, channel_id,
                                   'resolve', ts)
            SlackSdk.delete_message(token, channel_id, message_ts)

    return HttpResponse('')


def mod_flagged(data, action, moderation):

    if action == 'resolve':
        return mod_flagged_resolve(data, moderation)
    assert False, action


def save_moderation_action(moderation, username, channel_id,
                           action, message_id):
    moderation.status = channel_id
    moderation.status_reason = action
    moderation.message_id = message_id
    moderation.save()
    ModerationAction.objects.create(moderation=moderation,
                                    action=action,
                                    action_author_id=username)


def moderate(data):
    """
    """
    data = data.get('payload')
    data = json.loads(data)
    if data:

        action = data.get('actions')[0].get('value')
        message_id = data.get('message_ts')

        moderation = Moderation.objects.get_by_message_id(message_id)

        callback_id = data.get('callback_id')

        if callback_id == 'mod-inbox':
            return mod_inbox(data, action, moderation)

        elif callback_id == 'mod-flagged':
            return mod_flagged(data, action, moderation)

        return HttpResponse(json.dumps(data, indent=4))
