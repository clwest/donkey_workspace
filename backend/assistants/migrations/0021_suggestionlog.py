from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0020_assistantchatmessage_drift_score_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="SuggestionLog",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False,
                        serialize=False,
                    ),
                ),
                (
                    "trigger_type",
                    models.CharField(max_length=50, default="first_message_drift"),
                ),
                (
                    "anchor_slug",
                    models.CharField(max_length=100, blank=True, null=True),
                ),
                ("suggested_action", models.CharField(max_length=50)),
                ("score", models.FloatField(default=0.0)),
                ("status", models.CharField(max_length=20, default="pending")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "assistant",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="drift_suggestions",
                        to="assistants.assistant",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
