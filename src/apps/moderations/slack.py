import json
import requests

from datetime import datetime
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from .views import SlackSdk


@csrf_exempt
def interactions(request):
    slack_url = u'{base}'.format(
        base=reverse('social:begin', kwargs={'backend': 'slack'}),
    )

    slack = SlackSdk()

    context = {
        'slack_connect_url': slack_url,
        'data': slack.data,
    }

    if request.method == 'POST':
        # TODO: Remove static message
        text = ">New content! Educator <https://careervillage.org/users/1|Jared Chung> posted the <https://careervillage.org/questions/1234|answer> in response to <https://careervillage.org/questions/1234|What is the best way to focus for tests?>:\n>\"What I have tried to focus when taking tests is to not place to much pressure on myself. A test is simply a gauge of how you understand the test material. If you don't do well on a test, it gives you information on your progress. Having a good understanding of the materials is also very important. Many times the important skill is understanding how to take tests, so if you don't do well on a test, and you find out how the test answers were expected, you will have a better understanding for the next test. If you try to treat a test as if it is just another task, you may find the anxiety is lessened.\""
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

        response = slack.create_message(
            '#mod-inbox', text=text, attachments=attachments
        )

    return render_to_response('interactions.html',
                              context,
                              RequestContext(request))


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

    slack = SlackSdk()

    response = slack.create_message(
        '#mod-approved', text=text, attachments=attachments
    )

    ts = data.get('message_ts')
    slack.delete_message('#mod-inbox', ts)

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

    slack = SlackSdk()

    ts = data.get('message_ts')
    slack.update_message('#mod-inbox', ts, text=text, attachments=attachments)

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

    slack = SlackSdk()

    ts = data.get('message_ts')
    slack.update_message('#mod-inbox', ts, text=text, attachments=attachments)

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

    slack = SlackSdk()

    slack.create_message('#mod-flagged', text=text, attachments=attachments)

    ts = data.get('message_ts')
    slack.delete_message('#mod-inbox', ts)

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

    slack = SlackSdk()

    slack.create_message('#mod-resolved', text=text, attachments=attachments)

    ts = data.get('message_ts')
    slack.delete_message('#mod-flagged', ts)

    return HttpResponse('')


def mod_flagged(data):
    actions = data.get('actions')[0]
    action = actions.get('value')

    if action == 'resolve':
        return mod_flagged_resolve(data)


def moderation(request):
    payload = request.POST.get('payload')

    if payload:
        data = json.loads(payload)
        callback_id = data.get('callback_id')

        if callback_id == 'mod-inbox':
            return mod_inbox(data)

        elif callback_id == 'mod-flagged':
            return mod_flagged(data)

        return HttpResponse(json.dumps(data, indent=4))

    return HttpResponse('Hello world.')
