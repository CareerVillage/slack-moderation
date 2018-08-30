from background_task import background
from .slack import SlackSdk
from .models import Moderation

@background(schedule=10)
def post_moderation_async(moderation_id, data):
    slack = SlackSdk()
    print(moderation_id)
    response_data = slack.post_moderation(
        text=data['content'])
    print(response_data)
    message_id = response_data.get('ts')
    moderation = Moderation.objects.get(id=moderation_id)
    moderation.message_id = message_id
    moderation.save()