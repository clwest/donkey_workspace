from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0029_demo_usage_log"),
    ]

    operations = [
        migrations.AddField(
            model_name="demousagelog",
            name="demo_interaction_score",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="demousagelog",
            name="likely_to_convert",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="demousagelog",
            name="tips_helpful",
            field=models.IntegerField(default=0),
        ),
    ]
