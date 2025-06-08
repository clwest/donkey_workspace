from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0029_demo_usage_log"),
    ]

    operations = [
        migrations.AddField(
            model_name="assistant",
            name="prompt_notes",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="assistant",
            name="boosted_from_demo",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="assistant",
            name="boost_prompt_in_system",
            field=models.BooleanField(default=True),
        ),
    ]
