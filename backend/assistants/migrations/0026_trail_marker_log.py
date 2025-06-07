from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0025_spawn_metadata"),
        ("memory", "0011_replay_priority"),
    ]

    operations = [
        migrations.CreateModel(
            name="TrailMarkerLog",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("marker_type", models.CharField(max_length=50)),
                ("notes", models.TextField(blank=True, default="")),
                (
                    "assistant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="trail_markers",
                        to="assistants.assistant",
                    ),
                ),
                (
                    "related_memory",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="trail_markers",
                        to="memory.memoryentry",
                    ),
                ),
            ],
            options={"ordering": ["-timestamp"]},
        ),
    ]
