from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0033_demo_converted_from_demo"),
    ]

    operations = [
        migrations.AddField(
            model_name="assistant",
            name="mentor_assistant",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                related_name="mentees",
                to="assistants.assistant",
            ),
        ),
        migrations.AddField(
            model_name="assistant",
            name="mentor_for_demo_clone",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="assistant",
            name="nurture_started_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]

