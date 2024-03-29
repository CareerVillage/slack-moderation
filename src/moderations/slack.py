from datetime import datetime
import json
import pprint
import re
import requests
import traceback
from django.http import HttpResponse
from accounts.models import AuthToken
from moderations.models import Moderation, ModerationAction
from moderations.utils import timedelta_to_str
from .tasks import get_request_task

pp = pprint.PrettyPrinter(indent=4)


# Code this logic in a separate class that can be overwritten.
PRO_TIP_QUESTIONS = [
    "ProTip #1: Is this answer direct?",
    "ProTip #2: Is this answer comprehensive?",
    "ProTip #3: Does this answer use facts?",
    "ProTip #4: Does this answer tell a personal story?",
    "ProTip #5: Does this answer recommend next steps?",
    "ProTip #6: Does this answer cite sources?",
    "ProTip #7: Does this answer strike the right tone?",
    "ProTip #8: Does this answer use proper grammar, formatting, and structure?",
    "ProTip #9: Does this answer anticipate the student’s needs?",
    "ProTip #10: Is this answer concise?",
]

BEST_OF_THE_VILLAGE_THRESHOLD = 9
SUMMARY_TITLE = "ProTip Rating:"


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
    def get_messages_from_channel(channel, param='limit', param_value='2'):
        token, channel_id = SlackSdk.get_channel_data(channel)

        url = f'https://slack.com/api/conversations.history?{param}={param_value}'
        params = {
            'channel': channel_id,
        }

        response = get_request_task(url, params, token)
        response_json = response.json()
        messages = response_json['messages']
        if response_json['has_more']:
            extra_messages = SlackSdk.get_messages_from_channel(channel,
                                                                'cursor',
                                                                response_json['response_metadata']['next_cursor']
                                                                )
            messages = messages + extra_messages
        return messages

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

        token, channel_id = SlackSdk.get_channel_data('#mod-leaderboard')

        def post_leaderboard_on_slack(leaderboard, title, text=''):
            if title == 'All Time':
                text += (
                    '```\n'
                    'ALL TIME LEADERBOARD\n')
            else:
                text += (
                    '```\n'
                    'LAST WEEK LEADERBOARD\n')

            text += (
                '┌----------------------┬----------------------┐\n'
                '│ {0: <20} | {1: <20} │\n'
            ).format('Mod', title)

            sorted_leaderboard = sorted(list(leaderboard.items()),
                                        key=lambda x: x[1],
                                        reverse=True)

            count = 0
            for k, v in sorted_leaderboard:
                if k and k != 'ModBot':
                    text += '├----------------------┼----------------------┤\n'
                    text += '│ {0: <20} │ {1: <20} │\n'.format(k, v)

                    # Divide the table in multiple messages because it fails if the text/table is too long
                    count += 1
                    if count >= 20:
                        text += '```\n'
                        SlackSdk.create_message(token, channel_id,
                                                text, [], in_channel=True, is_async=True)
                        count = 0
                        text = '```\n'

            text += '└----------------------┴----------------------┘\n'
            text += '```\n'
            return SlackSdk.create_message(token, channel_id,
                                           text, [], in_channel=True, is_async=True)

        # Post on slack both tables
        post_leaderboard_on_slack(leaderboard['all_time'], 
                                  'All Time',
                                  "LEADERBOARD as of {date}\n".format(date=datetime.utcnow())
                                  )
        post_leaderboard_on_slack(leaderboard['seven_days'], 
                                  'Last 7 Days'
                                  )

        def avg(a, b):
            if b > 0.0:
                return a/float(b) * 100.0
            else:
                return 0

        # Post on slack both reports
        text = 'MOD TEAM SPEED REPORT AS OF {} UTC\n'.format(datetime.utcnow())
        text += '```\n'
        text += 'Average time to first mod review (all-time): %s over %i pieces of content\n' \
            % (timedelta_to_str(leaderboard['avg']['all_time']['review'][0]),
               leaderboard['avg']['all_time']['review'][2])

        text += '90th Percentile time to first mod review (all-time): %s over %i pieces of content\n' \
            % (timedelta_to_str(leaderboard['avg']['all_time']['review'][1]),
               leaderboard['avg']['all_time']['review'][2])

        text += 'Average time to first mod review (last 7 days): %s over %i pieces of content\n' \
            % (timedelta_to_str(leaderboard['avg']['seven_days']['review'][0]),
               leaderboard['avg']['seven_days']['review'][2])

        text += '90th Percentile time to first mod review (last 7 days): %s over %i pieces of content\n' \
            % (timedelta_to_str(leaderboard['avg']['seven_days']['review'][1]),
               leaderboard['avg']['seven_days']['review'][2])

        text += 'Average time to first mod resolution (all-time): %s over %i pieces of content\n' \
            % (timedelta_to_str(leaderboard['avg']['all_time']['resolution'][0]),
               leaderboard['avg']['all_time']['resolution'][1])

        text += 'Average time to first mod resolution (last 7 days): %s over %i pieces of content\n' \
            % (timedelta_to_str(leaderboard['avg']['seven_days']['resolution'][0]),
               leaderboard['avg']['seven_days']['resolution'][1])
        text += 'The oldest unmoderated piece of content is from: %s\n' % (leaderboard['last_unmoderated_content_date'])
        text += '```\n'

        text += 'CONTENT QUALITY REPORT AS OF {} UTC\n'.format(datetime.utcnow())
        counts = leaderboard['counts']
        text += '```\n'
        text += 'Past 7 days content: %i\n' % counts['total']

        text += 'Past 7 days flagged by mods: %i (%.2f%%)\n' \
            % (counts['total_flagged'],
               avg(counts['total_flagged'], counts['total']))

        urgent_total = counts['urgent'] if 'urgent' in counts else 0
        text += 'Reason: Urgent: %i (%.2f%% of flags)\n' \
            % (urgent_total,
               avg(urgent_total, counts['total_flagged']))

        ai_total = counts['AI'] if 'AI' in counts else 0
        text += 'Reason: AI: %i (%.2f%% of flags)\n' \
            % (ai_total,
               avg(ai_total, counts['total_flagged']))

        other_total = counts['other'] if 'other' in counts else 0
        text += 'Reason: Other: %i (%.2f%% of flags)\n' \
            % (other_total,
               avg(other_total, counts['total_flagged']))
        text += '```\n'

        return SlackSdk.create_message(token, channel_id,
                                       text, [], in_channel=True, is_async=True)

    @staticmethod
    def post_simple_leaderboard_timeframe(leaderboard, timeframe):
        token, channel_id = SlackSdk.get_channel_data('#mod-leaderboard')

        # Post on slack both reports
        text = f'MOD TEAM {timeframe.upper()} REPORT AS OF {datetime.utcnow()} UTC\n'
        text += '```\n'
        text += 'Average time to first mod review (%s): %s over %i pieces of content\n' \
            % (timeframe,
               timedelta_to_str(leaderboard['review']['average']),
               leaderboard['review']['count'])

        text += '90th Percentile time to first mod review (%s): %s over %i pieces of content\n' \
            % (timeframe,
               timedelta_to_str(leaderboard['review']['p90']),
               leaderboard['review']['count'])

        text += 'Average time to first mod resolution (%s): %s over %i pieces of content\n' \
            % (timeframe,
               timedelta_to_str(leaderboard['resolution']['average']),
               leaderboard['resolution']['count'])
        text += '```\n'

        return SlackSdk.create_message(token, channel_id,
                                       text, [], in_channel=True, is_async=True)

    @staticmethod
    def post_amount_of_msg_in_mod_inbox(mod_inbox_msg_count):
        token, channel_id = SlackSdk.get_channel_data('#mod-leaderboard')

        # Post on slack both reports
        text = f'There are {mod_inbox_msg_count} messages in the #mod-inbox channel'
        return SlackSdk.create_message(token, channel_id,
                                       text, [], in_channel=True, is_async=True)

    @staticmethod
    def create_message(access_token, channel_id,
                       text='', attachments=[], in_channel=False, is_async=False):

        try:

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
                'channel': channel_id,
                'text': text,
                'attachments': json.dumps(attachments),
                'unfurl_links': False,
                'unfurl_media': is_image,
            }
            if in_channel:
                params['response_type'] = 'in_channel'

            if not is_async:
                return requests.get(url='https://slack.com/api/chat.postMessage', 
                                    params=params, 
                                    headers={'Authorization': f'Bearer {access_token}'})
            else:
                return get_request_task('https://slack.com/api/chat.postMessage', params, access_token)
        except:
            print(traceback.format_exe())

    @staticmethod
    def delete_message(access_token, channel_id, ts):
        return get_request_task(url='https://slack.com/api/chat.delete',
                                params={
                                    'ts': ts,
                                    'channel': channel_id,
                                },
                                access_token=access_token)

    @staticmethod
    def update_message(access_token, channel_id, ts,
                       text='', attachments=[]):

        return get_request_task(url='https://slack.com/api/chat.update',
                                params={
                                    'ts': ts,
                                    'channel': channel_id,
                                    'text': text,
                                    'attachments': json.dumps(attachments),
                                    'parse': 'none',
                                },
                                access_token=access_token)


def is_answer(text):
    return 'posted the' in text and \
                'answer' in text and 'in response to' in text


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
    print('Channel: ', channel_id)
    response = SlackSdk.create_message(token, channel_id, text, attachments)
    print('Reponse: ', response.status_code)
    if response.status_code == 200:
        data = response.json()
        print('Data: ', data)
        if data.get('ok'):
            token, channel_id = SlackSdk.get_channel_data('#mod-inbox')
            print('save moderation action')
            save_moderation_action(moderation, approved_by, channel_id,
                                   'approve', data.get('ts'))
            print('Delete message -> ')
            response = SlackSdk.delete_message(token, channel_id, ts)
            print('Response ', response)

            if is_answer(text):
                send_to_approved_advice(data, moderation)

    return HttpResponse('')


def send_to_approved_advice(data, moderation):

    try:

        attachments = []
        for question_index, question in enumerate(PRO_TIP_QUESTIONS):
            attachment = {
                'fallback': "Moderator actions",
                'callback_id': 'mod-approved-advice',
                'text': question,
                'attachment_type': 'default',
                'actions': [
                    {
                        'name': 'yes',
                        'text': "Yes",
                        'type': 'button',
                        'value': 'pro-tip-yes-{}'.format(question_index),
                        'style': 'primary'
                    },
                    {
                        'name': 'no',
                        'text': "No",
                        'type': 'button',
                        'value': 'pro-tip-no-{}'.format(question_index)
                    }
                ]
            }

            attachments.append(attachment)

        attachment = {
            'fallback': "Moderator actions",
            'callback_id': 'mod-approved-advice',
            'title': SUMMARY_TITLE,
            'text': "You have currently positively marked {} out of {} ProTips".format(0, len(PRO_TIP_QUESTIONS)),
            'attachment_type': 'default',
        }
        attachments.append(attachment)

        text = data.get('message').get('text')
        token, channel_id = SlackSdk.get_channel_data('#approved-advice')
        response = SlackSdk.create_message(token, channel_id, text, attachments)
    except:
        print(traceback.format_exc())


def mod_pro_tip(data, moderation, current_question_index, response):

    try:

        original_message = data.get('original_message')
        text = original_message.get('text')
        ts = data.get('message_ts')

        attachments = []
        summary = None
        answer_count = 0
        yes_count = 1 if response == 'yes' else 0
        for question_index, attachment in enumerate(
                original_message.get('attachments')):

            # count partial results
            actions = attachment.get('actions')
            if actions:
                action = actions[0]
                value = action['value']
                if 'pro-tip-change' in value:
                    answer_count += 1
                    if 'yes' in value:
                        yes_count += 1

            print('--------------------')
            pp.pprint(attachment)

            if attachment.get('title') == SUMMARY_TITLE:
                summary = attachment

            if current_question_index == question_index:
                if response in ['yes', 'no']:
                    actions = [
                        {
                            'name': 'change',
                            'text': "Change your response ({})".format(response),
                            'type': 'button',
                            'value': 'pro-tip-change-{}-{}'.format(response, question_index),
                            'style': 'primary'
                        }
                    ]
                else:
                    actions = [
                        {
                            'name': 'yes',
                            'text': "Yes",
                            'type': 'button',
                            'value': 'pro-tip-yes-{}'.format(question_index),
                            'style': 'primary'
                        },
                        {
                            'name': 'no',
                            'text': "No",
                            'type': 'button',
                            'value': 'pro-tip-no-{}'.format(question_index)
                        }
                    ]
                attachment_data = {
                    'fallback': "Moderator actions",
                    'callback_id': 'mod-approved-advice',
                    'text': PRO_TIP_QUESTIONS[question_index],
                    'attachment_type': 'default',
                    'actions': actions,
                }
                attachments.append(attachment_data)
            else:
                attachments.append(attachment)

        print('-------------------------------')
        print('Attachments: (before lambda)')
        pp.pprint(attachments)

        attachments = [item for item in attachments if item.get('title') != SUMMARY_TITLE]

        print('-------------------------------')
        print('Attachments: (before summary)')
        pp.pprint(attachments)

        print('******************** Yes Count:')
        print(yes_count)
        print('********* summary (old)')
        print(summary['text'])

        summary['text'] = "You have currently positively marked " + str(yes_count) + " out of 10 ProTips"

        if answer_count == len(PRO_TIP_QUESTIONS) - 1 and \
                response in ['yes', 'no']:
            actions = [
                {
                    'name': 'submit',
                    'text': "Submit your review",
                    'type': 'button',
                    'value': 'pro-tip-submit',
                    'style': 'primary'
                }
            ]
            summary['actions'] = actions
        else:
            if 'actions' in summary:
                del summary['actions']

        attachments.append(summary)

        print('-------------------------------')
        print('Attachments: (after summary)')
        pp.pprint(attachments)

        token, channel_id = SlackSdk.get_channel_data('#approved-advice')
        SlackSdk.update_message(token, channel_id,
                                ts, text=text, attachments=attachments)

    except:
        print(traceback.format_exc())


def mod_submit(data, moderation):

    try:

        original_message = data.get('original_message')
        text = original_message.get('text')
        ts = data.get('message_ts')

        yes_count = 0
        for question_index, attachment in enumerate(
                original_message.get('attachments')):

            # count partial results
            actions = attachment.get('actions')
            if actions:
                action = actions[0]
                value = action['value']
                if 'pro-tip-change' in value:
                    if 'yes' in value:
                        yes_count += 1

        reviewed_by = data.get('user').get('name')
        reviewed_time = float(data.get('action_ts').split('.')[0])
        reviewed_time = datetime.utcfromtimestamp(reviewed_time)
        reviewed_time = reviewed_time.strftime('%Y-%m-%d %I:%M%p')
        message_ts = data.get('message_ts')

        attachments = [
            {
                'fallback': 'Please moderate this.',
                'text': '%s UTC: @%s reviewed this advice' %
                        (reviewed_time, reviewed_by),
                'callback_id': 'mod-approved-advice',
                'attachment_type': 'default',
                'mrkdwn_in': [
                    'text'
                ]
            }
        ]

        if yes_count >= BEST_OF_THE_VILLAGE_THRESHOLD:
            channel_id = '#best-of-village'

            actions = [
                {
                    'name': 'submit',
                    'text': "Approve",
                    'type': 'button',
                    'value': 'pro-tip-approve',
                    'style': 'primary'
                }
            ]

            attachments[0]['actions'] = actions

        else:
            channel_id = '#quality-assessed'

        token, channel_id = SlackSdk.get_channel_data(channel_id)
        response = SlackSdk.create_message(token, channel_id, text=text,
                                           attachments=attachments)

        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                token, channel_id = SlackSdk.get_channel_data('#approved-advice')
                ts = data.get('ts')

                SlackSdk.delete_message(token, channel_id, message_ts)

        return HttpResponse('')

    except:
        print(traceback.format_exc())


def mod_approve(data, moderation):

    try:

        original_message = data.get('original_message')
        text = original_message.get('text')
        approved_by = data.get('user').get('name')
        approved_time = float(data.get('action_ts').split('.')[0])
        approved_time = datetime.utcfromtimestamp(approved_time)
        approved_time = approved_time.strftime('%Y-%m-%d %I:%M%p')
        attachment = original_message.get('attachments')[0]
        ts = data.get('message_ts')

        attachment['actions'] = []
        attachments = [
            attachment,
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

        token, channel_id = SlackSdk.get_channel_data('#best-of-village')
        response = SlackSdk.update_message(token, channel_id, ts,
                                           text=text, attachments=attachments)

        return HttpResponse('')

    except:
        print(traceback.format_exc())


def mod_inbox_reject(data, moderation):

    original_message = data.get('original_message')
    text = original_message.get('text')
    ts = data.get('message_ts')

    attachments = [
        {
            'fallback': 'Moderator actions',
            'text': '_Reject: Select a reason_',
            'callback_id': 'mod-inbox',
            'attachment_type': 'default',
            'mrkdwn_in': [
                'text'
            ],
            'actions': [
                {
                    'name': 'Urgent',
                    'text': 'Urgent',
                    'type': 'button',
                    'value': 'urgent',
                    'style': 'danger'
                },
                {
                    'name': 'AI',
                    'text': 'AI',
                    'type': 'button',
                    'value': 'AI',
                    'style': 'danger'
                },
                {
                    'name': 'Other',
                    'text': 'Other',
                    'type': 'button',
                    'value': 'other',
                    'style': 'danger'
                },
                {
                    'name': 'Undo',
                    'text': 'Undo',
                    'type': 'button',
                    'value': 'undo'
                }
            ]
        }
    ]

    token, channel_id = SlackSdk.get_channel_data('#mod-inbox')
    SlackSdk.update_message(token, channel_id, ts, text=text, attachments=attachments)

    return HttpResponse('')


def mod_inbox_reject_undo(data):
    original_message = data.get('original_message')
    text = original_message.get('text')
    ts = data.get('message_ts')

    attachments = [
        {
            'fallback': 'Moderator actions',
            'callback_id': 'mod-inbox',
            'attachment_type': 'default',
            'actions': [
                {
                    'name': 'approve',
                    'text': 'Approve',
                    'type': 'button',
                    'value': 'approve',
                    'style': 'primary'
                },
                {
                    'name': 'reject',
                    'text': 'Reject',
                    'type': 'button',
                    'value': 'reject'
                }
            ]
        }
    ]

    token, channel_id = SlackSdk.get_channel_data('#mod-inbox')
    SlackSdk.update_message(token, channel_id,
                            ts, text=text, attachments=attachments)

    return HttpResponse('')


def mod_inbox_reject_reason(data, moderation, channel_to_send):
    original_message = data.get('original_message')
    text = original_message.get('text')
    rejected_by = data.get('user').get('name')
    rejected_time = float(data.get('action_ts').split('.')[0])
    rejected_time = datetime.utcfromtimestamp(rejected_time)
    rejected_time = rejected_time.strftime('%Y-%m-%d %I:%M%p')
    rejected_reason = data.get('actions')[0]['value']
    emoji = ':fire:' if rejected_reason == 'urgent' else ''
    ts = data.get('message_ts')

    attachments = [
        {
            'fallback': 'Moderator actions',
            'text': f'_{rejected_time} UTC: @{rejected_by} rejected this with the reason: \'{rejected_reason}\' {emoji}_',
            'callback_id': channel_to_send,
            'attachment_type': 'default',
            'mrkdwn_in': ['text'],
            'actions': [
                {
                    'name': 'Resolve',
                    'text': 'Mark resolved',
                    'type': 'button',
                    'value': 'resolve',
                    'style': 'primary'
                }
            ]
        }
    ]

    token, channel_id = SlackSdk.get_channel_data(f'#{channel_to_send}')

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

    elif (action == 'urgent') or (action == 'other'):
        return mod_inbox_reject_reason(data, moderation, 'mod-flagged')
    elif action == 'AI':
        return mod_inbox_reject_reason(data, moderation, 'mod-suspected-ai')


def mod_approved_advice(data, action, moderation):

    try:
        if action.startswith('pro-tip-yes') or \
                action.startswith('pro-tip-no') or \
                action.startswith('pro-tip-change'):
            question_index = int(action[-1])
            response = action[:-2].replace('pro-tip-', '')

            return mod_pro_tip(data, moderation, question_index, response)

        if action == 'pro-tip-submit':

            return mod_submit(data, moderation)

        elif action == 'pro-tip-approve':

            return mod_approve(data, moderation)

    except:
        print(traceback.format_exc())


def mod_flagged_resolve(data, moderation, origin_channel):
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
            'fallback': 'Please moderate this.',
            'text': '%s\n_%s UTC: @%s marked this \'Resolved\'_' %
                    (rejected_reason, resolved_time, resolved_by),
            'callback_id': 'mod-resolved',
            'attachment_type': 'default',
            'mrkdwn_in': [
                'text'
            ]
        }
    ]

    token, channel_id = SlackSdk.get_channel_data('#mod-resolved')
    response = SlackSdk.create_message(token, channel_id, text=text,
                                       attachments=attachments)

    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):

            token, channel_id = SlackSdk.get_channel_data(f'#{origin_channel}')
            ts = data.get('ts')

            save_moderation_action(moderation, resolved_by, channel_id,
                                   'resolve', ts)
            SlackSdk.delete_message(token, channel_id, message_ts)

    return HttpResponse('')


def mod_flagged(data, action, moderation, origin_channel):
    if action == 'resolve':
        return mod_flagged_resolve(data, moderation, origin_channel)
    assert False, action


def save_moderation_action(moderation, username, channel_id,
                           action, message_id):
    if moderation:
        moderation.status = channel_id
        moderation.status_reason = action
        moderation.message_id = message_id
        moderation.save()
        ModerationAction.objects.create(moderation=moderation,
                                        action=action,
                                        action_author_id=username)


def moderate(data):
    """"
    """
    data = data.get('payload')
    data = json.loads(data)
    print(data)
    if data:

        action = data.get('actions')[0].get('value')
        message_id = data.get('message_ts')

        moderation = Moderation.objects.get_by_message_id(message_id)

        callback_id = data.get('callback_id')

        if callback_id == 'mod-inbox':
            return mod_inbox(data, action, moderation)
        if callback_id == 'mod-approved-advice':
            return mod_approved_advice(data, action, moderation)
        elif callback_id == 'mod-flagged':
            return mod_flagged(data, action, moderation, 'mod-flagged')
        elif callback_id == 'mod-suspected-ai':
            return mod_flagged(data, action, moderation, 'mod-suspected-ai')

        return HttpResponse(json.dumps(data, indent=4))
