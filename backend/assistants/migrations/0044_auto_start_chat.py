from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0043_trust_signal_log"),
    ]

    operations = [
        migrations.AddField(
            model_name="assistant",
            name="auto_start_chat",
            field=models.BooleanField(default=True),
        ),
    ]
