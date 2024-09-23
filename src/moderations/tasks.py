import json

import requests
from django.conf import settings

from moderation.celery import app as celery_app


@celery_app.task
def mark_new_user_content_as_approved(node_id):
    url = f"{settings.CV_BASE_URL}/api/v2/internal/moderation/approve_node/"
    payload = {
        "node_id": node_id,
    }
    headers = {
        "Authorization": f"Api-Key {settings.CV_MODERATION_API_KEY}",
        "Content-type": "application/json",
    }

    requests.post(url, data=json.dumps(payload), headers=headers)
