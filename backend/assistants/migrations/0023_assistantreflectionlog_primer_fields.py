from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0022_tourstartlog"),
    ]

    operations = [
        migrations.AddField(
            model_name="assistantreflectionlog",
            name="is_primer",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="assistantreflectionlog",
            name="generated_from_memory_ids",
            field=models.JSONField(default=list, blank=True),
        ),
    ]

