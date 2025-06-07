from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0022_tourstartlog"),
    ]

    operations = [
        migrations.AddField(
            model_name="assistant",
            name="intro_text",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="assistant",
            name="archetype_summary",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="assistant",
            name="show_intro_splash",
            field=models.BooleanField(default=True),
        ),
    ]
