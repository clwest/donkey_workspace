from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0040_demo_reflection_note"),
    ]

    operations = [
        migrations.AddField(
            model_name="demousagelog",
            name="comparison_variant",
            field=models.CharField(max_length=50, blank=True, default=""),
        ),
    ]
