from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("memory", "0012_trail_summary_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="ragplaybacklog",
            name="demo_session_id",
            field=models.CharField(max_length=64, blank=True, default=""),
        ),
    ]
