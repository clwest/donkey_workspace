from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0035_demousagelog_user_fk"),
    ]

    operations = [
        migrations.AddField(
            model_name="assistant",
            name="growth_stage",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="assistant",
            name="growth_points",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="assistant",
            name="growth_unlocked_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
