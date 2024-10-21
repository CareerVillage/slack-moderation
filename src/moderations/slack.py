import json
import pprint
import re
import traceback
from datetime import datetime, timezone

from django.conf import settings
from django.http import HttpResponse
from slack_bolt import App

from moderations.models import Moderation, ModerationAction
from moderations.tasks import mark_new_user_content_as_approved
from moderations.utils import timedelta_to_str

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


app = App(
    process_before_response=True,
    token=settings.SLACK_BOT_OAUTH_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET,
)


class SlackSdk(object):
    @staticmethod
    def _get_channel_id(name: str) -> str:
        return settings.CHANNEL_IDS_DICT[name]

    @staticmethod
    def get_messages_from_channel(channel_name, param="limit", param_value="999"):
        channel_id = SlackSdk._get_channel_id(channel_name)

        if param == "limit":
            response = app.client.conversations_history(
                channel=channel_id, limit=param_value
            )
        elif param == "cursor":
            response = app.client.conversations_history(
                channel=channel_id, cursor=param_value
            )

        response_json = response.data
        messages = response_json["messages"]
        # In case there are more messages than the limit, recursively get the rest
        if response_json["has_more"]:
            extra_messages = SlackSdk.get_messages_from_channel(
                channel_name,
                "cursor",
                response_json["response_metadata"]["next_cursor"],
            )
            messages = messages + extra_messages
        return messages

    @staticmethod
    def post_moderation(moderation, data):
        slack_channel = (
            "new-user-content" if data.get("new_user_content") else "mod-inbox"
        )
        text = data["content"]
        attachments = [
            {
                "fallback": "Moderator actions",
                "callback_id": slack_channel,
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "approve",
                        "text": "Approve",
                        "type": "button",
                        "value": "approve",
                        "style": "primary",
                    },
                    {
                        "name": "reject",
                        "text": "Reject",
                        "type": "button",
                        "value": "reject",
                    },
                ],
            }
        ]

        channel_id = SlackSdk._get_channel_id(slack_channel)
        response = SlackSdk.create_message(channel_id, text, attachments)
        json_response = response.data

        message_id = json_response.get("ts")
        moderation.message_id = message_id
        moderation.save()

        return json_response

    @staticmethod
    def post_leaderboard(leaderboard):
        """
        leaderboard = [
            {'@jared': 12,345},
        ]
        """

        channel_id = SlackSdk._get_channel_id("mod-leaderboard")

        def post_leaderboard_on_slack(leaderboard, title, text=""):
            if title == "All Time":
                text += "```\n" "ALL TIME LEADERBOARD\n"
            else:
                text += "```\n" "LAST WEEK LEADERBOARD\n"

            text += (
                "┌----------------------┬----------------------┐\n"
                "│ {0: <20} | {1: <20} │\n"
            ).format("Mod", title)

            sorted_leaderboard = sorted(
                list(leaderboard.items()), key=lambda x: x[1], reverse=True
            )

            count = 0
            for k, v in sorted_leaderboard:
                if k and k != "ModBot":
                    text += "├----------------------┼----------------------┤\n"
                    text += "│ {0: <20} │ {1: <20} │\n".format(k, v)

                    # Divide the table in multiple messages because it fails if the text/table is too long
                    count += 1
                    if count >= 20:
                        text += "```\n"
                        SlackSdk.create_message(channel_id, text, [], in_channel=True)
                        count = 0
                        text = "```\n"

            text += "└----------------------┴----------------------┘\n"
            text += "```\n"
            return SlackSdk.create_message(channel_id, text, [], in_channel=True)

        # Post on slack both tables
        post_leaderboard_on_slack(
            leaderboard["all_time"],
            "All Time",
            "LEADERBOARD as of {date}\n".format(date=datetime.now(tz=timezone.utc)),
        )
        post_leaderboard_on_slack(leaderboard["seven_days"], "Last 7 Days")

        def avg(a, b):
            return a / float(b) * 100.0 if b > 0.0 else 0

        # Post on slack both reports
        text = "MOD TEAM SPEED REPORT AS OF {} UTC\n".format(
            datetime.now(tz=timezone.utc)
        )
        text += "```\n"
        text += (
            "Average time to first mod review (all-time): %s over %i pieces of content\n"
            % (
                timedelta_to_str(leaderboard["avg"]["all_time"]["review"][0]),
                leaderboard["avg"]["all_time"]["review"][2],
            )
        )

        text += (
            "90th Percentile time to first mod review (all-time): %s over %i pieces of content\n"
            % (
                timedelta_to_str(leaderboard["avg"]["all_time"]["review"][1]),
                leaderboard["avg"]["all_time"]["review"][2],
            )
        )

        text += (
            "Average time to first mod review (last 7 days): %s over %i pieces of content\n"
            % (
                timedelta_to_str(leaderboard["avg"]["seven_days"]["review"][0]),
                leaderboard["avg"]["seven_days"]["review"][2],
            )
        )

        text += (
            "90th Percentile time to first mod review (last 7 days): %s over %i pieces of content\n"
            % (
                timedelta_to_str(leaderboard["avg"]["seven_days"]["review"][1]),
                leaderboard["avg"]["seven_days"]["review"][2],
            )
        )

        text += (
            "Average time to first mod resolution (all-time): %s over %i pieces of content\n"
            % (
                timedelta_to_str(leaderboard["avg"]["all_time"]["resolution"][0]),
                leaderboard["avg"]["all_time"]["resolution"][1],
            )
        )

        text += (
            "Average time to first mod resolution (last 7 days): %s over %i pieces of content\n"
            % (
                timedelta_to_str(leaderboard["avg"]["seven_days"]["resolution"][0]),
                leaderboard["avg"]["seven_days"]["resolution"][1],
            )
        )
        text += "The oldest unmoderated piece of content is from: %s\n" % (
            leaderboard["last_unmoderated_content_date"]
        )
        text += "```\n"

        text += "CONTENT QUALITY REPORT AS OF {} UTC\n".format(
            datetime.now(tz=timezone.utc)
        )
        counts = leaderboard["counts"]
        text += "```\n"
        text += "Past 7 days content: %i\n" % counts["total"]

        text += "Past 7 days flagged by mods: %i (%.2f%%)\n" % (
            counts["total_flagged"],
            avg(counts["total_flagged"], counts["total"]),
        )

        urgent_total = counts["urgent"] if "urgent" in counts else 0
        text += "Reason: Urgent: %i (%.2f%% of flags)\n" % (
            urgent_total,
            avg(urgent_total, counts["total_flagged"]),
        )

        ai_total = counts["AI"] if "AI" in counts else 0
        text += "Reason: AI: %i (%.2f%% of flags)\n" % (
            ai_total,
            avg(ai_total, counts["total_flagged"]),
        )

        other_total = counts["other"] if "other" in counts else 0
        text += "Reason: Other: %i (%.2f%% of flags)\n" % (
            other_total,
            avg(other_total, counts["total_flagged"]),
        )
        text += "```\n"

        return SlackSdk.create_message(channel_id, text, [], in_channel=True)

    @staticmethod
    def post_simple_leaderboard_timeframe(leaderboard, timeframe):
        channel_id = SlackSdk._get_channel_id("mod-leaderboard")

        # Post on slack both reports
        text = f"MOD TEAM {timeframe.upper()} REPORT AS OF {datetime.now(tz=timezone.utc)} UTC\n"
        text += "```\n"
        text += (
            "Average time to first mod review (%s): %s over %i pieces of content\n"
            % (
                timeframe,
                timedelta_to_str(leaderboard["review"]["average"]),
                leaderboard["review"]["count"],
            )
        )

        text += (
            "90th Percentile time to first mod review (%s): %s over %i pieces of content\n"
            % (
                timeframe,
                timedelta_to_str(leaderboard["review"]["p90"]),
                leaderboard["review"]["count"],
            )
        )

        text += (
            "Average time to first mod resolution (%s): %s over %i pieces of content\n"
            % (
                timeframe,
                timedelta_to_str(leaderboard["resolution"]["average"]),
                leaderboard["resolution"]["count"],
            )
        )
        text += "```\n"

        return SlackSdk.create_message(channel_id, text, [], in_channel=True)

    @staticmethod
    def post_amount_of_msg_in_mod_inbox(mod_inbox_msg_count):
        channel_id = SlackSdk._get_channel_id("mod-leaderboard")

        # Post on slack both reports
        text = f"There are {mod_inbox_msg_count} messages in the #mod-inbox channel"
        return SlackSdk.create_message(channel_id, text, [], in_channel=True)

    @staticmethod
    def create_message(channel_id, text="", attachments=[], in_channel=False):
        try:
            is_image = "https://res.cloudinary.com/" in text

            if len(text) >= 3500:
                search_text = re.findall(
                    r"^(.* posted the) <(https://.*)\|(.*)>.*:\n", text
                )
                if search_text:
                    new_content_text = search_text[0][0]
                    link = search_text[0][1]
                    new_content_type = search_text[0][2]
                    text = (
                        "%s %s. WARNING: this content cannot be displayed, "
                        "please read the complete content <%s|HERE>"
                        % (new_content_text, new_content_type, link)
                    )

            params = {
                "channel": channel_id,
                "text": text,
                "attachments": json.dumps(attachments),
                "unfurl_links": False,
                "unfurl_media": is_image,
            }
            if in_channel:
                params["response_type"] = "in_channel"

            return app.client.chat_postMessage(**params)
        except Exception as e:
            print(e)

    @staticmethod
    def delete_message(channel_id, ts):
        return app.client.chat_delete(channel=channel_id, ts=ts)

    @staticmethod
    def update_message(channel_id, ts, text="", attachments=[]):
        return app.client.chat_update(
            channel=channel_id, ts=ts, text=text, attachments=attachments, parse="none"
        )


def is_answer(text):
    return ("posted the" in text) and ("answer" in text) and ("in response to" in text)


def mod_inbox_approved(data, moderation, origin_channel):
    original_message = data.get("original_message")
    text = original_message.get("text")
    approved_by = data.get("user").get("name")
    approved_time = float(data.get("action_ts").split(".")[0])
    approved_time = datetime.fromtimestamp(approved_time, tz=timezone.utc)
    approved_time = approved_time.strftime("%Y-%m-%d %I:%M%p")
    ts = data.get("message_ts")

    attachments = [
        {
            "fallback": "Please moderate this.",
            "text": ":white_check_mark: _Approved by @%s %s UTC_"
            % (approved_by, approved_time),
            "callback_id": "mod-approved",
            "attachment_type": "default",
            "mrkdwn_in": ["text"],
        }
    ]

    channel_id = SlackSdk._get_channel_id("mod-approved")
    response = SlackSdk.create_message(channel_id, text, attachments)

    if response.status_code == 200:
        data = response.data
        if data.get("ok"):
            channel_id = SlackSdk._get_channel_id(origin_channel)
            # Save the moderation action
            save_moderation_action(
                moderation, approved_by, channel_id, "approve", data.get("ts")
            )
            # Delete the message from mod-inbox or new-user-content
            SlackSdk.delete_message(channel_id, ts)

            # If the message was in new-user-content, mark it as approved in QA database
            if origin_channel == "new-user-content":
                mark_new_user_content_as_approved.delay(moderation.content_key)

            if is_answer(text):
                send_to_approved_advice(data)

    return HttpResponse("")


def send_to_approved_advice(data):
    try:
        attachments = []
        for question_index, question in enumerate(PRO_TIP_QUESTIONS):
            attachment = {
                "fallback": "Moderator actions",
                "callback_id": "mod-approved-advice",
                "text": question,
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "yes",
                        "text": "Yes",
                        "type": "button",
                        "value": "pro-tip-yes-{}".format(question_index),
                        "style": "primary",
                    },
                    {
                        "name": "no",
                        "text": "No",
                        "type": "button",
                        "value": "pro-tip-no-{}".format(question_index),
                    },
                ],
            }
            attachments.append(attachment)

        attachment = {
            "fallback": "Moderator actions",
            "callback_id": "mod-approved-advice",
            "title": SUMMARY_TITLE,
            "text": "You have currently positively marked {} out of {} ProTips".format(
                0, len(PRO_TIP_QUESTIONS)
            ),
            "attachment_type": "default",
        }
        attachments.append(attachment)

        text = data.get("message").get("text")
        channel_id = SlackSdk._get_channel_id("approved-advice")
        SlackSdk.create_message(channel_id, text, attachments)
    except:
        print(traceback.format_exc())


def mod_pro_tip(data, current_question_index, response):
    try:
        original_message = data.get("original_message")
        text = original_message.get("text")
        ts = data.get("message_ts")

        attachments = []
        summary = None
        answer_count = 0
        yes_count = 1 if response == "yes" else 0
        for question_index, attachment in enumerate(
            original_message.get("attachments")
        ):
            # count partial results
            actions = attachment.get("actions")
            if actions:
                action = actions[0]
                value = action["value"]
                if "pro-tip-change" in value:
                    answer_count += 1
                    if "yes" in value:
                        yes_count += 1

            print("--------------------")
            pp.pprint(attachment)

            if attachment.get("title") == SUMMARY_TITLE:
                summary = attachment

            if current_question_index == question_index:
                if response in ["yes", "no"]:
                    actions = [
                        {
                            "name": "change",
                            "text": "Change your response ({})".format(response),
                            "type": "button",
                            "value": "pro-tip-change-{}-{}".format(
                                response, question_index
                            ),
                            "style": "primary",
                        }
                    ]
                else:
                    actions = [
                        {
                            "name": "yes",
                            "text": "Yes",
                            "type": "button",
                            "value": "pro-tip-yes-{}".format(question_index),
                            "style": "primary",
                        },
                        {
                            "name": "no",
                            "text": "No",
                            "type": "button",
                            "value": "pro-tip-no-{}".format(question_index),
                        },
                    ]
                attachment_data = {
                    "fallback": "Moderator actions",
                    "callback_id": "mod-approved-advice",
                    "text": PRO_TIP_QUESTIONS[question_index],
                    "attachment_type": "default",
                    "actions": actions,
                }
                attachments.append(attachment_data)
            else:
                attachments.append(attachment)

        print("-------------------------------")
        print("Attachments: (before lambda)")
        pp.pprint(attachments)

        attachments = [
            item for item in attachments if item.get("title") != SUMMARY_TITLE
        ]

        print("-------------------------------")
        print("Attachments: (before summary)")
        pp.pprint(attachments)

        print("******************** Yes Count:")
        print(yes_count)
        print("********* summary (old)")
        print(summary["text"])

        summary["text"] = (
            "You have currently positively marked "
            + str(yes_count)
            + " out of 10 ProTips"
        )

        if answer_count == len(PRO_TIP_QUESTIONS) - 1 and response in ["yes", "no"]:
            actions = [
                {
                    "name": "submit",
                    "text": "Submit your review",
                    "type": "button",
                    "value": "pro-tip-submit",
                    "style": "primary",
                }
            ]
            summary["actions"] = actions
        else:
            if "actions" in summary:
                del summary["actions"]

        attachments.append(summary)

        print("-------------------------------")
        print("Attachments: (after summary)")
        pp.pprint(attachments)

        channel_id = SlackSdk._get_channel_id("approved-advice")
        SlackSdk.update_message(channel_id, ts, text=text, attachments=attachments)

    except:
        print(traceback.format_exc())


def mod_submit(data):
    try:
        original_message = data.get("original_message")
        text = original_message.get("text")

        yes_count = 0
        for question_index, attachment in enumerate(
            original_message.get("attachments")
        ):
            # count partial results
            actions = attachment.get("actions")
            if actions:
                action = actions[0]
                value = action["value"]
                if "pro-tip-change" in value:
                    if "yes" in value:
                        yes_count += 1

        reviewed_by = data.get("user").get("name")
        reviewed_time = float(data.get("action_ts").split(".")[0])
        reviewed_time = datetime.fromtimestamp(reviewed_time, tz=timezone.utc)
        reviewed_time = reviewed_time.strftime("%Y-%m-%d %I:%M%p")
        message_ts = data.get("message_ts")

        attachments = [
            {
                "fallback": "Please moderate this.",
                "text": "%s UTC: @%s reviewed this advice"
                % (reviewed_time, reviewed_by),
                "callback_id": "mod-approved-advice",
                "attachment_type": "default",
                "mrkdwn_in": ["text"],
            }
        ]

        if yes_count >= BEST_OF_THE_VILLAGE_THRESHOLD:
            channel_id = "best-of-village"

            actions = [
                {
                    "name": "submit",
                    "text": "Approve",
                    "type": "button",
                    "value": "pro-tip-approve",
                    "style": "primary",
                }
            ]

            attachments[0]["actions"] = actions

        else:
            channel_id = "quality-assessed"

        channel_id = SlackSdk._get_channel_id(channel_id)
        response = SlackSdk.create_message(
            channel_id, text=text, attachments=attachments
        )

        if response.status_code == 200:
            data = response.data
            if data.get("ok"):
                channel_id = SlackSdk._get_channel_id("approved-advice")
                SlackSdk.delete_message(channel_id, message_ts)

        return HttpResponse("")

    except:
        print(traceback.format_exc())


def mod_approve(data):
    try:
        original_message = data.get("original_message")
        text = original_message.get("text")
        approved_by = data.get("user").get("name")
        approved_time = float(data.get("action_ts").split(".")[0])
        approved_time = datetime.fromtimestamp(approved_time, tz=timezone.utc)
        approved_time = approved_time.strftime("%Y-%m-%d %I:%M%p")
        attachment = original_message.get("attachments")[0]
        ts = data.get("message_ts")

        attachment["actions"] = []
        attachments = [
            attachment,
            {
                "fallback": "Please moderate this.",
                "text": ":white_check_mark: _Approved by @%s %s UTC_"
                % (approved_by, approved_time),
                "callback_id": "mod-approved",
                "attachment_type": "default",
                "mrkdwn_in": ["text"],
            },
        ]

        channel_id = SlackSdk._get_channel_id("best-of-village")
        SlackSdk.update_message(channel_id, ts, text=text, attachments=attachments)

        return HttpResponse("")

    except:
        print(traceback.format_exc())


def mod_inbox_reject(data, origin_channel):
    original_message = data.get("original_message")
    text = original_message.get("text")
    ts = data.get("message_ts")

    attachments = [
        {
            "fallback": "Moderator actions",
            "text": "_Reject: Select a reason_",
            "callback_id": origin_channel,
            "attachment_type": "default",
            "mrkdwn_in": ["text"],
            "actions": [
                {
                    "name": "Urgent",
                    "text": "Urgent",
                    "type": "button",
                    "value": "urgent",
                    "style": "danger",
                },
                {
                    "name": "AI",
                    "text": "AI",
                    "type": "button",
                    "value": "AI",
                    "style": "danger",
                },
                {
                    "name": "Other",
                    "text": "Other",
                    "type": "button",
                    "value": "other",
                    "style": "danger",
                },
                {"name": "Undo", "text": "Undo", "type": "button", "value": "undo"},
            ],
        }
    ]

    channel_id = SlackSdk._get_channel_id(origin_channel)
    SlackSdk.update_message(channel_id, ts, text=text, attachments=attachments)

    return HttpResponse("")


def mod_inbox_reject_undo(data, origin_channel):
    original_message = data.get("original_message")
    text = original_message.get("text")
    ts = data.get("message_ts")

    attachments = [
        {
            "fallback": "Moderator actions",
            "callback_id": origin_channel,
            "attachment_type": "default",
            "actions": [
                {
                    "name": "approve",
                    "text": "Approve",
                    "type": "button",
                    "value": "approve",
                    "style": "primary",
                },
                {
                    "name": "reject",
                    "text": "Reject",
                    "type": "button",
                    "value": "reject",
                },
            ],
        }
    ]

    channel_id = SlackSdk._get_channel_id(origin_channel)
    SlackSdk.update_message(channel_id, ts, text=text, attachments=attachments)

    return HttpResponse("")


def mod_inbox_reject_reason(data, moderation, origin_channel, channel_to_send):
    original_message = data.get("original_message")
    text = original_message.get("text")
    rejected_by = data.get("user").get("name")
    rejected_time = float(data.get("action_ts").split(".")[0])
    rejected_time = datetime.fromtimestamp(rejected_time, tz=timezone.utc)
    rejected_time = rejected_time.strftime("%Y-%m-%d %I:%M%p")
    rejected_reason = data.get("actions")[0]["value"]
    emoji = ":fire:" if rejected_reason == "urgent" else ""
    ts = data.get("message_ts")

    attachments = [
        {
            "fallback": "Moderator actions",
            "text": f"_{rejected_time} UTC: @{rejected_by} rejected this with the reason: '{rejected_reason}' {emoji}_",
            "callback_id": channel_to_send,
            "attachment_type": "default",
            "mrkdwn_in": ["text"],
            "actions": [
                {
                    "name": "Resolve",
                    "text": "Mark resolved",
                    "type": "button",
                    "value": "resolve",
                    "style": "primary",
                }
            ],
        }
    ]

    channel_id = SlackSdk._get_channel_id(f"{channel_to_send}")
    response = SlackSdk.create_message(channel_id, text=text, attachments=attachments)

    if response.status_code == 200:
        data = response.data
        if data.get("ok"):
            channel_id = SlackSdk._get_channel_id(origin_channel)

            save_moderation_action(
                moderation, rejected_by, channel_id, rejected_reason, data.get("ts")
            )

            SlackSdk.delete_message(channel_id, ts)

    return HttpResponse("")


def mod_inbox(data, action, moderation, origin_channel):
    if action == "approve":
        return mod_inbox_approved(data, moderation, origin_channel)

    elif action == "reject":
        return mod_inbox_reject(data, origin_channel)

    elif action == "undo":
        return mod_inbox_reject_undo(data, origin_channel)

    elif (action == "urgent") or (action == "other"):
        return mod_inbox_reject_reason(
            data, moderation, origin_channel, channel_to_send="mod-flagged"
        )
    elif action == "AI":
        return mod_inbox_reject_reason(
            data, moderation, origin_channel, channel_to_send="mod-suspected-ai"
        )


def mod_approved_advice(data, action):
    try:
        if (
            action.startswith("pro-tip-yes")
            or action.startswith("pro-tip-no")
            or action.startswith("pro-tip-change")
        ):
            question_index = int(action[-1])
            response = action[:-2].replace("pro-tip-", "")

            return mod_pro_tip(data, question_index, response)

        elif action == "pro-tip-submit":
            return mod_submit(data)

        elif action == "pro-tip-approve":
            return mod_approve(data)

    except:
        print(traceback.format_exc())


def mod_flagged_resolve(data, moderation, origin_channel):
    original_message = data.get("original_message")
    text = original_message.get("text")
    resolved_by = data.get("user").get("name")
    resolved_time = float(data.get("action_ts").split(".")[0])
    resolved_time = datetime.fromtimestamp(resolved_time, tz=timezone.utc)
    resolved_time = resolved_time.strftime("%Y-%m-%d %I:%M%p")
    rejected_reason = original_message.get("attachments")[0]["text"]
    message_ts = data.get("message_ts")

    attachments = [
        {
            "fallback": "Please moderate this.",
            "text": "%s\n_%s UTC: @%s marked this 'Resolved'_"
            % (rejected_reason, resolved_time, resolved_by),
            "callback_id": "mod-resolved",
            "attachment_type": "default",
            "mrkdwn_in": ["text"],
        }
    ]

    channel_id = SlackSdk._get_channel_id("mod-resolved")
    response = SlackSdk.create_message(channel_id, text=text, attachments=attachments)

    if response.status_code == 200:
        data = response.data
        if data.get("ok"):
            channel_id = SlackSdk._get_channel_id(f"{origin_channel}")
            ts = data.get("ts")

            save_moderation_action(moderation, resolved_by, channel_id, "resolve", ts)
            SlackSdk.delete_message(channel_id, message_ts)

    return HttpResponse("")


def mod_flagged(data, action, moderation, origin_channel):
    if action == "resolve":
        return mod_flagged_resolve(data, moderation, origin_channel)
    assert False, action


def save_moderation_action(moderation, username, channel_id, action, message_id):
    if moderation:
        moderation.status = channel_id
        moderation.status_reason = action
        moderation.message_id = message_id
        moderation.save()
        ModerationAction.objects.create(
            moderation=moderation, action=action, action_author_id=username
        )


def moderate(data):
    """ " """
    data = data.get("payload")
    data = json.loads(data)

    if settings.DEBUG:
        print(data)

    if data:
        action = data.get("actions")[0].get("value")
        message_id = data.get("message_ts")

        moderation = Moderation.objects.get_by_message_id(message_id)

        callback_id = data.get("callback_id")

        if callback_id == "mod-inbox" or callback_id == "new-user-content":
            return mod_inbox(data, action, moderation, callback_id)
        elif callback_id == "mod-approved-advice":
            return mod_approved_advice(data, action)
        elif callback_id == "mod-flagged" or callback_id == "mod-suspected-ai":
            return mod_flagged(data, action, moderation, callback_id)

        return HttpResponse(json.dumps(data, indent=4))
