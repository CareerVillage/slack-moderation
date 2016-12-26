from datetime import timedelta
from django.utils import timezone
from .models import ModerationAction


def get_leaderboard():
    """
    """

    all_time = {}
    seven_days = {}
    actions = ModerationAction.objects.all().select_related('moderation')

    all_time_review_time = []
    all_time_resolution_time = []
    seven_days_review_time = []
    seven_days_resolution_time = []

    counts = {
        'total': 0,
        'total_flagged': 0,
        'off_topic': 0,
        'inappropriate': 0,
        'contact_info': 0,
        'other': 0,
    }

    for action in actions:
        aid = action.action_author_id
        all_time.setdefault(aid, 0)
        all_time[aid] += 1
        if action.created_at > timezone.now() - timedelta(days=7):
            seven_days.setdefault(aid, 0)
            seven_days[aid] += 1

            if action.action == 'moderate':
                counts['total'] += 1

            if action.action in ['off_topic', 'inappropriate',
                                 'contact_info', 'other']:
                counts['total_flagged'] += 1
                counts[action.action] += 1

            if action.action in ['approve', 'reject']:
                seven_days_review_time.append(action.created_at - action.moderation.created_at)
            elif action.action == 'resolve':
                seven_days_resolution_time.append(action.created_at - action.moderation.created_at)

        if action.action in ['approve', 'reject']:
            all_time_review_time.append(action.created_at - action.moderation.created_at)
        elif action.action == 'resolve':
            all_time_resolution_time.append(action.created_at - action.moderation.created_at)

    def avg(time_list):
        if time_list:
            return sum(time_list, timedelta()) / len(time_list)
        else:
            return timedelta()

    return {
        'all_time': all_time,
        'seven_days': seven_days,
        'avg': {
            'all_time': {
                'review': (avg(all_time_review_time), len(all_time_review_time)),
                'resolution': (avg(all_time_resolution_time), len(all_time_resolution_time)),
            },
            'seven_days': {
                'review': (avg(seven_days_review_time), len(seven_days_review_time)),
                'resolution': (avg(seven_days_resolution_time), len(seven_days_resolution_time)),
            },
        },
        'counts': counts,
    }
