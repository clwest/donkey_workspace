from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("memory", "0005_rag_playback"),
    ]

    operations = [
        migrations.AddField(
            model_name="ragplaybacklog",
            name="query_term",
            field=models.CharField(max_length=255, blank=True, default=""),
        ),
        migrations.AddField(
            model_name="ragplaybacklog",
            name="score_cutoff",
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="ragplaybacklog",
            name="fallback_reason",
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="ragplaybacklog",
            name="playback_type",
            field=models.CharField(
                max_length=20,
                choices=[("reflection", "Reflection"), ("replay", "Replay"), ("manual", "Manual")],
                default="manual",
            ),
        ),
    ]
