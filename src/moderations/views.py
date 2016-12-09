from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Moderation, ModerationAction
from .serializers import ModerationSerializer
from .slack import SlackSdk, moderate


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
        print data
        moderation = Moderation.objects.create_or_update(
            content_key=data['content_key'],
            content=data['content'],
            content_author_id=data['content_author_id'],
            last_action=data['action'])
        serializer.moderation = moderation

        content = serializer.validated_data.get('content')
        ModerationAction.objects.create(moderation=moderation)

        slack = SlackSdk()

        response = slack.post_moderation(
            text=content)

        print response

@api_view(['POST'])
def slack_response(request):

    data = request.data

    return moderate(data)
