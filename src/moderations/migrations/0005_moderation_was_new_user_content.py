# Generated by Django 5.1 on 2024-09-05 20:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("moderations", "0004_moderation_content_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="moderation",
            name="was_new_user_content",
            field=models.BooleanField(default=False),
        ),
    ]