from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0039_demo_overlay_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="demosessionlog",
            name="demo_reflection_note",
            field=models.TextField(blank=True),
        ),
    ]
