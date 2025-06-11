from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("agents", "0001_initial"),
        ("intel_core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SymbolicAgentInsightLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                (
                    "symbol",
                    models.CharField(max_length=100),
                ),
                (
                    "conflict_score",
                    models.FloatField(default=0.0),
                ),
                (
                    "resolution_method",
                    models.CharField(blank=True, max_length=100),
                ),
                (
                    "notes",
                    models.TextField(blank=True),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "agent",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="insight_logs", to="agents.agent"),
                ),
                (
                    "document",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="insight_logs", to="intel_core.document"),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]

