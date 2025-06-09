from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0042_drift_refinement_log"),
    ]

    operations = [
        migrations.CreateModel(
            name="TrustSignalLog",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                (
                    "assistant",
                    models.ForeignKey(
                        to="assistants.assistant",
                        on_delete=models.CASCADE,
                        related_name="trust_signals",
                    ),
                ),
                ("key", models.CharField(max_length=50)),
                ("value", models.FloatField(null=True, blank=True)),
                ("label", models.CharField(max_length=100, blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
