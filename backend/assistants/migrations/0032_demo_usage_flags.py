from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0031_featured_assistants"),
    ]

    operations = [
        migrations.AddField(
            model_name="demousagelog",
            name="recap_shown",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="demousagelog",
            name="feedback_submitted",
            field=models.BooleanField(default=False),
        ),
    ]
