from django.db import migrations, models
import django.contrib.postgres.fields

class Migration(migrations.Migration):
    dependencies = [
        ("memory", "0003_reflection_score"),
    ]

    operations = [
        migrations.AddField(
            model_name="reflectionreplaylog",
            name="replayed_summary",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="reflectionreplaylog",
            name="drift_reason",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="reflectionreplaylog",
            name="status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("accepted", "Accepted"), ("skipped", "Skipped")],
                default="pending",
                max_length=20,
            ),
        ),
    ]
