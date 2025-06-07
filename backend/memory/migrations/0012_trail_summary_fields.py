from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("memory", "0011_replay_priority"),
    ]

    operations = [
        migrations.AddField(
            model_name="memoryentry",
            name="is_summary",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="memoryentry",
            name="memory_type",
            field=models.CharField(max_length=50, blank=True, default=""),
        ),
    ]
