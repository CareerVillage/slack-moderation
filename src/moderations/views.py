from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Moderation, ModerationAction
from .serializers import ModerationSerializer
from .slack import SlackSdk, moderate
from .stats import get_leaderboard


class ModerationActionModelViewSet(viewsets.ModelViewSet):
    """
    Receive post from client /moderations/node
    Save moderation request to database
    Send message to slack
    """
    queryset = ModerationAction.objects.all()
    serializer_class = ModerationSerializer

    def perform_create(self, serializer):
        """Override method in order to include interaction with Slack
           Save moderation to database
           Send message to Slack
        """
        data = serializer.validated_data

        slack = SlackSdk()
        response_data = slack.post_moderation(
            text=data['content'])

        message_id = response_data.get('ts')

        moderation = Moderation.objects.create(
            content_key=data['content_key'],
            content=data['content'],
            content_author_id=data['content_author_id'],
            status='#modinbox',
            status_reason='moderate',
            message_id=message_id
        )
        serializer.moderation = moderation

        ModerationAction.objects.create(moderation=moderation,
                                        action='moderate')


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
