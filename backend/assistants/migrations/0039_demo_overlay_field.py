from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0038_demo_reflection_flag"),
    ]

    operations = [
        migrations.AddField(
            model_name="demousagelog",
            name="reflection",
            field=models.ForeignKey(
                to="assistants.assistantreflectionlog",
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
            ),
        ),
    ]
