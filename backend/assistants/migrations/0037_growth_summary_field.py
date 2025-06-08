from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0036_growth_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="assistant",
            name="growth_summary_memory",
            field=models.ForeignKey(
                to="memory.memoryentry",
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                related_name="growth_summaries",
            ),
        ),
    ]

