from django.db import migrations, models
from django.conf import settings
import uuid

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0021_suggestionlog"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssistantTourStartLog",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("source", models.CharField(max_length=50, default="dashboard")),
                ("assistant", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="tour_start_logs", to="assistants.assistant")),
                ("user", models.ForeignKey(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-started_at"]},
        ),
        migrations.AlterUniqueTogether(
            name="assistanttourstartlog",
            unique_together={("user", "assistant")},
        ),
    ]
