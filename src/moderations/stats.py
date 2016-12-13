from datetime import timedelta
from django.utils import timezone
from .models import ModerationAction


def get_leaderboard():
    """
    """

    all_time = {}
    seven_days = {}
    actions = ModerationAction.objects.all()
    for action in actions:
        aid = action.action_author_id
        all_time.setdefault(aid, 0)
        all_time[aid] += 1
        if action.created_at > timezone.now() - timedelta(days=7):
            seven_days.setdefault(aid, 0)
            seven_days[aid] += 1

    return {'all_time': all_time, 'seven_days': seven_days}

