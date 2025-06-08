from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0030_demo_session_log"),
    ]

    operations = [
        migrations.AddField(
            model_name="assistant",
            name="is_featured",
            field=models.BooleanField(default=False, help_text="Showcase this demo assistant on the demos page"),
        ),
        migrations.AddField(
            model_name="assistant",
            name="featured_rank",
            field=models.IntegerField(null=True, blank=True, help_text="Ordering for featured assistants"),
        ),
    ]
