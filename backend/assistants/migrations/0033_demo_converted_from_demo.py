from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0032_demo_usage_flags"),
    ]

    operations = [
        migrations.AddField(
            model_name="demousagelog",
            name="converted_from_demo",
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
