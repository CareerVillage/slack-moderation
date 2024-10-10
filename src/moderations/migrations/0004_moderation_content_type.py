# Generated by Django 5.1 on 2024-09-05 15:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("moderations", "0003_moderation_moderations_content_1a0145_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="moderation",
            name="content_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("answer", "answer"),
                    ("question", "question"),
                    ("comment", "comment"),
                    ("thankyoucomment", "thankyoucomment"),
                    ("profileanswer", "profileanswer"),
                    ("answerstep", "answerstep"),
                    ("todolist", "todolist"),
                    ("todo", "todo"),
                    ("careergoalstatement", "careergoalstatement"),
                    ("profileimage", "profileimage"),
                    ("questiontag", "questiontag"),
                    ("useraboutprofile", "useraboutprofile"),
                ],
                max_length=50,
                null=True,
            ),
        ),
    ]
