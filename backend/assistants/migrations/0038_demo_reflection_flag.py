from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0037_growth_summary_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="assistantreflectionlog",
            name="demo_reflection",
            field=models.BooleanField(default=False),
        ),
    ]
