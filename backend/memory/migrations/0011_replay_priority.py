from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("memory", "0010_anchor_stability_priority"),
    ]

    operations = [
        migrations.AddField(
            model_name="reflectionreplaylog",
            name="is_priority",
            field=models.BooleanField(default=False),
        ),
    ]
