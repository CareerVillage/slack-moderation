import os

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moderation.settings.base")

app = Celery("moderation")

app.config_from_object(settings, namespace="CELERY")
app.conf.update(
    task_serializer="pickle",
    result_serializer="pickle",
    accept_content=["json", "pickle"],  # Ignore other content
)
app.autodiscover_tasks()
