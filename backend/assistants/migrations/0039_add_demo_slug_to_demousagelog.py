from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0038_demo_reflection_flag"),
    ]

    operations = [
        migrations.AddField(
            model_name="demousagelog",
            name="demo_slug",
            field=models.CharField(max_length=100, default=""),
            preserve_default=False,
        ),
    ]
