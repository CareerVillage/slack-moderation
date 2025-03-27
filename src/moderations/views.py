import time

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Moderation, ModerationAction
from .permissions import HasModerationApiKey
from .serializers import ModerationSerializer
from .slack import SlackSdk, mod_inbox_approved, mod_inbox_reject_reason, moderate
from .stats import get_leaderboard, get_simple_leaderboard_num_weeks


class ModerationActionModelViewSet(viewsets.ModelViewSet):
    """
    Receive post from client /moderations/node
    Save moderation request to database
    Send message to slack
    """

    queryset = ModerationAction.objects.all()
    serializer_class = ModerationSerializer
    permission_classes = (HasModerationApiKey,)

    def list(self, request):
        content_id = self.request.query_params.get("contentId", None)
        if content_id is not None:
            queryset = ModerationAction.objects.filter(
                moderation__content_key=content_id
            )
        else:
            queryset = ModerationAction.objects.filter(pk=1)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def _modbot_action(self, action, mod_obj, msg_text, origin_channel):
        data_for_mod_bot = {
            "original_message": {"text": msg_text},
            "user": {"name": "ModBot"},
            "action_ts": str(time.time()),
            "actions": [{"value": "Other"}],
            "message_ts": Moderation.objects.get(id=mod_obj.id).message_id,
        }
        if action == "approve":
            mod_inbox_approved(data_for_mod_bot, mod_obj, origin_channel)
        elif action == "fake_approve":
            # Fake approve is used to move a message to mod-approved without actually approving it
            # Without doing mark_new_user_content_as_approved() in the end
            mod_inbox_approved(
                data_for_mod_bot, mod_obj, origin_channel, fake_approve=True
            )
        elif action == "flag":
            mod_inbox_reject_reason(
                data_for_mod_bot, mod_obj, origin_channel, channel_to_send="mod-flagged"
            )

    def perform_create(self, serializer):
        """Override method in order to include interaction with Slack
        Save moderation to database
        Send message to Slack
        """
        data = serializer.validated_data

        # Temporary fix while we discover why we receive duplicated messages
        duplicated = Moderation.objects.filter(
            content_key=data["content_key"], content=data["content"]
        ).exists()

        if duplicated:
            print(
                f"Duplicated message recieved but not sent: id:{data['content_key']} "
                + f"content:{data['content']} author_id:{data['content_author_id']}"
            )
        else:
            # Check if there is already a message in mod-inbox with the same node_id,
            # if there is, send it to mod_approved
            # This was done to exclude moderation after answer edited by AI
            channel_name = (
                "new-user-content" if data["new_user_content"] else "mod-inbox"
            )
            status = f"#{channel_name}"

            try:
                old_node = Moderation.objects.get(
                    content_key=data["content_key"], status=status
                )
                # We don't want to actually approve it, only move it to the mod-approved channel
                # If we approve it, content from new_user_content will get marked as approved_to_be_showned,
                # so people could approved their own questions by editing them (CV-1187)
                self._modbot_action(
                    "fake_approve",
                    old_node,
                    old_node.content,
                    origin_channel=channel_name,
                )
            except ObjectDoesNotExist:
                pass

            moderation = Moderation.objects.create(
                content_key=data["content_key"],
                content_type=data["content_type"],
                content=data["content"],
                content_author_id=data["content_author_id"],
                status=status,
                status_reason="moderate",
                was_new_user_content=data["new_user_content"],
            )

            SlackSdk.post_moderation(moderation=moderation, data=data)

            ModerationAction.objects.create(moderation=moderation, action="moderate")

            if data["auto_approve"] is True:
                self._modbot_action(
                    "approve", moderation, data["content"], channel_name
                )
            elif data["auto_flag"] is True:
                self._modbot_action("flag", moderation, data["content"], channel_name)


@api_view(["POST"])
def slack_response(request):
    data = request.data
    return moderate(data)


@api_view(["POST"])
def generate_stats(request):
    leaderboard = get_leaderboard()
    slack = SlackSdk()
    slack.post_leaderboard(leaderboard)
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def generate_stats_okr(request):
    leaderboard = get_simple_leaderboard_num_weeks(weeks=12)
    slack = SlackSdk()
    slack.post_simple_leaderboard_timeframe(leaderboard, timeframe="last OKR")
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def generate_stats_3w(request):
    leaderboard = get_simple_leaderboard_num_weeks(weeks=3)
    slack = SlackSdk()
    slack.post_simple_leaderboard_timeframe(leaderboard, timeframe="last 3 weeks")
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def generate_mod_inbox_status(request):
    slack = SlackSdk()
    mod_inbox_msg_count = len(slack.get_messages_from_channel("mod-inbox"))
    slack.post_amount_of_msg_in_particular_channel("mod-inbox", mod_inbox_msg_count)

    new_user_content_msg_count = len(
        slack.get_messages_from_channel("new-user-content")
    )
    slack.post_amount_of_msg_in_particular_channel(
        "new-user-content", new_user_content_msg_count
    )
    return Response(status=status.HTTP_200_OK)
