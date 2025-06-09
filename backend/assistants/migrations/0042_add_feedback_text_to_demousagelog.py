from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0041_add_comparison_variant_to_demousagelog"),
    ]

    operations = [
        migrations.AddField(
            model_name="demousagelog",
            name="feedback_text",
            field=models.TextField(blank=True),
        ),
    ]
