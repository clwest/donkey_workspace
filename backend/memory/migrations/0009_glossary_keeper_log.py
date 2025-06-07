from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("memory", "0008_display_tooltip_location"),
    ]

    operations = [
        migrations.CreateModel(
            name="GlossaryKeeperLog",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                (
                    "anchor",
                    models.ForeignKey(on_delete=models.CASCADE, related_name="keeper_logs", to="memory.symbolicmemoryanchor"),
                ),
                (
                    "assistant",
                    models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to="assistants.assistant"),
                ),
                ("action_taken", models.CharField(max_length=64)),
                ("score_before", models.FloatField(default=0.0)),
                ("score_after", models.FloatField(default=0.0)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
