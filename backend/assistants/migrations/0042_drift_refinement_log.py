from django.db import migrations, models
import uuid

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0041_add_comparison_variant_to_demousagelog"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssistantDriftRefinementLog",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ("assistant", models.ForeignKey(to="assistants.assistant", on_delete=models.CASCADE, related_name="drift_refinement_logs")),
                ("session_id", models.CharField(max_length=64, blank=True, default="")),
                ("glossary_terms", models.JSONField(default=list, blank=True)),
                ("prompt_sections", models.JSONField(default=list, blank=True)),
                ("tone_tags", models.JSONField(default=list, blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
