

from datetime import timedelta
from src.moderations.slack import SlackSdk
from django.db.models import Avg, Count, F
from django.utils import timezone
from moderations.models import ModerationAction, Moderation


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
    all_time_review_time_avg = ModerationAction.objects.filter(action__in=moderation_actions).annotate(
        time_to_approve=F('created_at') - F('moderation__created_at')).values(
        'action', 'time_to_approve').aggregate(Avg('time_to_approve'))['time_to_approve__avg']

    all_time_resolution_count = ModerationAction.objects.filter(action='resolve').count()
    all_time_resolution_time_avg = ModerationAction.objects.filter(action='resolve').annotate(
        time_to_approve=F('created_at') - F('moderation__created_at')).values(
        'action', 'time_to_approve').aggregate(Avg('time_to_approve'))['time_to_approve__avg']


    seven_days_review_count = ModerationAction.objects.filter(action__in=moderation_actions, created_at__gte=timezone.now() - timedelta(days=7)).count()
    seven_days_review_time_avg = ModerationAction.objects.filter(action__in=moderation_actions,  created_at__gte=timezone.now() - timedelta(days=7)).annotate(
        time_to_approve=F('created_at') - F('moderation__created_at')).values(
        'action', 'time_to_approve').aggregate(Avg('time_to_approve'))['time_to_approve__avg']

    seven_days_resolution_count = ModerationAction.objects.filter(action='resolve', created_at__gte=timezone.now() - timedelta(days=7)).count()
    seven_days_resolution_time_avg = ModerationAction.objects.filter(action='resolve', created_at__gte=timezone.now() - timedelta(days=7)).annotate(
        time_to_approve=F('created_at') - F('moderation__created_at')).values(
        'action', 'time_to_approve').aggregate(Avg('time_to_approve'))['time_to_approve__avg']


  
    counts = {}
    counts['total_flagged'] = 0
    totals = ModerationAction.objects.values('action').annotate(total=Count('action'))
    for total in totals:
        action = total['action']
        total = total['total']
        if action == 'moderate':
            counts['total'] = total
        elif action in flag_actions:
            counts['total_flagged'] += total
            counts[action] = total 
    
    all_messages = SlackSdk.get_all_messages_of_channel('#mod-inbox')
    list_of_ts = list_of_ts = [message['ts'] for message in all_messages]
    last_unmoderated_content_date = Moderation.objects.filter(message_id__in=list_of_ts).order_by('created_at')[0].created_at.strftime('%Y-%m-%d')

    return {
        'all_time': all_time,
        'seven_days': seven_days,
        'avg': {
            'all_time': {
                'review': (all_time_review_time_avg, all_time_review_count),
                'resolution': (all_time_resolution_time_avg, all_time_review_count),
            },
            'seven_days': {
                'review': (seven_days_review_time_avg, seven_days_review_count),
                'resolution': (seven_days_resolution_time_avg, seven_days_resolution_count),
            },
        },
        'counts': counts,
        'last_unmoderated_content_date': last_unmoderated_content_date,
    }
