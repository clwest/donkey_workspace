from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0027_trail_recap_flag"),
    ]

    operations = [
        migrations.AddField(
            model_name="trailmarkerlog",
            name="user_note",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trailmarkerlog",
            name="user_emotion",
            field=models.CharField(max_length=16, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trailmarkerlog",
            name="is_starred",
            field=models.BooleanField(default=False),
        ),
    ]
