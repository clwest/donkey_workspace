from django.db import migrations, models
import uuid

class Migration(migrations.Migration):
    dependencies = [
        ("memory", "0004_replay_diff_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="RAGPlaybackLog",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ("assistant", models.ForeignKey(on_delete=models.CASCADE, related_name="rag_playbacks", to="assistants.assistant")),
                ("query", models.TextField()),
                ("memory_context", models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to="mcp_core.memorycontext")),
                ("chunks", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddField(
            model_name="reflectionreplaylog",
            name="rag_playback",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name="replay_logs", to="memory.ragplaybacklog"),
        ),
    ]
