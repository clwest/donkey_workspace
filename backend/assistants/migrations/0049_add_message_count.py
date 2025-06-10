from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0048_add_started_at_to_demousagelog"),
    ]

    operations = [
        migrations.AddField(
            model_name="demousagelog",
            name="message_count",
            field=models.IntegerField(default=0),
        ),
    ]
