import math
import functools
from datetime import timedelta
from django.db.models import Avg, Count, F
from django.utils import timezone
from .slack import SlackSdk
from moderations.models import ModerationAction, Moderation


def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values

    This pure-python implementation of percentiles requires only the standard
    library and Pyhon 2.7+. Source: http://code.activestate.com/recipes/511478/
    """
    if not N:
        return None
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0+d1


def get_leaderboard():
    """
    """

    moderation_actions = [
        'approve',
        'inappropriate',
        'contact_info',
        'other',
        'off_topic',
    ]

    flag_actions = [
        'inappropriate',
        'contact_info',
        'other',
        'off_topic',
    ]

    actions = ModerationAction.objects.filter(action__in=moderation_actions).values(
        'action_author_id').annotate(total=Count('action_author_id')).order_by('-total')

    all_time = {}
    for item in actions:
        all_time[item['action_author_id']] = item['total']


    actions = ModerationAction.objects.filter(
        action__in=moderation_actions, created_at__gte=timezone.now() - timedelta(days=7)).values(
        'action_author_id').annotate(
        total=Count('action_author_id')).order_by('-total')

    seven_days = {}
    for item in actions:
        seven_days[item['action_author_id']] = item['total']


    all_time_review_count = ModerationAction.objects.filter(action__in=moderation_actions).count()
    all_time_review_time_avg = ModerationAction.objects.filter(
            action__in=moderation_actions
        ).exclude(
            action_author_id='ModBot'
        ).annotate(
            time_to_approve=F('created_at') - F('moderation__created_at')
        ).values(
            'time_to_approve'
        ).aggregate(Avg('time_to_approve'))['time_to_approve__avg']
    all_time_reviews = ModerationAction.objects.filter(
            action__in=moderation_actions
        ).exclude(action_author_id='ModBot').annotate(
            time_to_approve=F('created_at') - F('moderation__created_at')
        ).values_list('time_to_approve', flat=True)
    all_time_review_time_p90_in_seconds = percentile(
            sorted(all_time_reviews),
            percent= 0.9, # 90th percentile
            key= lambda x:x.total_seconds()
        )
    all_time_review_time_p90 = timedelta(seconds=all_time_review_time_p90_in_seconds)

    all_time_resolution_count = ModerationAction.objects.filter(action='resolve').count()
    all_time_resolution_time_avg = ModerationAction.objects.filter(action='resolve').annotate(
        time_to_approve=F('created_at') - F('moderation__created_at')).values(
        'action', 'time_to_approve').aggregate(Avg('time_to_approve'))['time_to_approve__avg']

    seven_days_review_count = ModerationAction.objects.filter(action__in=moderation_actions,
            created_at__gte=timezone.now() - timedelta(days=7)).exclude(action_author_id='ModBot').count()
    seven_days_review_time_avg = ModerationAction.objects.filter(action__in=moderation_actions,
            created_at__gte=timezone.now() - timedelta(days=7)).exclude(action_author_id='ModBot').annotate(
            time_to_approve=F('created_at') - F('moderation__created_at')
            ).values('time_to_approve').aggregate(Avg('time_to_approve'))['time_to_approve__avg']
    seven_days_reviews = ModerationAction.objects.filter(
            action__in=moderation_actions,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).exclude(
            action_author_id='ModBot'
        ).annotate(
            time_to_approve=F('created_at') - F('moderation__created_at')
        ).values_list('time_to_approve', flat=True)
    seven_days_review_time_p90_in_seconds = percentile(
            sorted(seven_days_reviews),
            percent= 0.9, # 90th percentile
            key= lambda x:x.total_seconds()
        )
    seven_days_review_time_p90 = timedelta(seconds=seven_days_review_time_p90_in_seconds)

    seven_days_resolution_count = ModerationAction.objects.filter(action='resolve', created_at__gte=timezone.now() - timedelta(days=7)).count()
    seven_days_resolution_time_avg = ModerationAction.objects.filter(action='resolve', created_at__gte=timezone.now() - timedelta(days=7)).annotate(
        time_to_approve=F('created_at') - F('moderation__created_at')).values(
        'action', 'time_to_approve').aggregate(Avg('time_to_approve'))['time_to_approve__avg']

    counts = {}
    counts['total_flagged'] = 0
    totals = (ModerationAction.objects
              .filter(created_at__gte=timezone.now() - timedelta(days=7))
              .values('action')
              .annotate(total=Count('action'))
              )
    for total in totals:
        action = total['action']
        total = total['total']
        if action == 'moderate':
            counts['total'] = total
        elif action in flag_actions:
            counts['total_flagged'] += total
            counts[action] = total

    slack = SlackSdk()

    list_of_ts_in_mod_inbox = [message['ts'] for message in slack.get_all_messages_of_channel('#mod-inbox')]
    messages_in_mod_inbox = Moderation.objects.filter(message_id__in=list_of_ts_in_mod_inbox).order_by('created_at')
    if messages_in_mod_inbox:
        last_unmoderated_content_date = messages_in_mod_inbox[0].created_at.strftime('%Y-%m-%d')
    else:
        last_unmoderated_content_date = 'Currently, there is no unmoderated content'

    return {
        'all_time': all_time,
        'seven_days': seven_days,
        'avg': {
            'all_time': {
                'review': (all_time_review_time_avg, all_time_review_time_p90, all_time_review_count),
                'resolution': (all_time_resolution_time_avg, all_time_review_count),
            },
            'seven_days': {
                'review': (seven_days_review_time_avg, seven_days_review_time_p90, seven_days_review_count),
                'resolution': (seven_days_resolution_time_avg, seven_days_resolution_count),
            },
        },
        'counts': counts,
        'last_unmoderated_content_date': last_unmoderated_content_date,
    }
