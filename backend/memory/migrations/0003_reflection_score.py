from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("memory", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="reflectionreplaylog",
            name="reflection_score",
            field=models.FloatField(default=0.0),
        ),
    ]

