import logging
import time

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Moderation, ModerationAction
from .serializers import ModerationSerializer
from .slack import SlackSdk, moderate, mod_inbox_approved, mod_inbox_reject_reason
from .stats import get_leaderboard, get_simple_leaderboard_num_weeks
from .tasks import post_moderation_task


class ModerationActionModelViewSet(viewsets.ModelViewSet):
    """
    Receive post from client /moderations/node
    Save moderation request to database
    Send message to slack
    """
    queryset = ModerationAction.objects.all()
    serializer_class = ModerationSerializer

    def list(self, request):
        content_id = self.request.query_params.get('contentId', None)
        if not content_id is None:
            queryset = ModerationAction.objects.filter(moderation__content_key=content_id)
        else:
            queryset = ModerationAction.objects.filter(pk=1)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)
        

    def perform_create(self, serializer):
        """Override method in order to include interaction with Slack
           Save moderation to database
           Send message to Slack
        """
        data = serializer.validated_data
        
        # Temporary fix while we discover why we receive duplicated messages
        duplicated = False
        old_objs = Moderation.objects.filter(content_key=data['content_key']).values_list('content', flat=True)
        if old_objs and old_objs[0] == data['content']:
            duplicated = True
            print(f"Duplicated message recieved but not sent: id:{data['content_key']} content:{data['content']} author_id:{data['content_author_id']}")

        if not duplicated:
            moderation = Moderation.objects.create(
                content_key=data['content_key'],
                content=data['content'],
                content_author_id=data['content_author_id'],
                status='#modinbox',
                status_reason='moderate'
            )

            post_moderation_task(moderation_id=moderation.id, data=data)

            ModerationAction.objects.create(moderation=moderation, action='moderate')

            print('------')
            print(data)
            print('------')

            if data['auto_approve'] is True or data['auto_flag'] is True:
                data_for_mod_bot = {
                    'original_message': {
                        'text': data['content']
                    },
                    'user': {
                        'name': 'ModBot'
                    },
                    'action_ts': str(time.time()),
                    'actions': [
                        {
                            'value': 'Other'
                        }
                    ],
                    'message_ts': Moderation.objects.get(id=moderation.id).message_id,
                }

                if data['auto_approve'] == True:
                    mod_inbox_approved(data_for_mod_bot, moderation)
                elif data['auto_flag'] == True:
                    mod_inbox_reject_reason(data_for_mod_bot, moderation)          


@api_view(['POST'])
def slack_response(request):

    data = request.data

    return moderate(data)


@api_view(['POST'])
def generate_stats(request):
    leaderboard = get_leaderboard()
    slack = SlackSdk()
    slack.post_leaderboard(leaderboard)
    return Response('')


@api_view(['POST'])
def generate_stats_okr(request):
    leaderboard = get_simple_leaderboard_num_weeks(weeks=12)
    slack = SlackSdk()
    slack.post_simple_leaderboard_timeframe(leaderboard, timeframe='last OKR')
    return Response('')


@api_view(['POST'])
def generate_stats_3w(request):
    leaderboard = get_simple_leaderboard_num_weeks(weeks=3)
    slack = SlackSdk()
    slack.post_simple_leaderboard_timeframe(leaderboard, timeframe='last 3 weeks')
    return Response('')
