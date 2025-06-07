from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0026_trail_marker_log"),
    ]

    operations = [
        migrations.AddField(
            model_name="assistant",
            name="show_trail_recap",
            field=models.BooleanField(default=False),
        ),
    ]
