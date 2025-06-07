from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0023_intro_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="assistant",
            name="demo_slug",
            field=models.SlugField(unique=True, null=True, blank=True, max_length=100),
        ),
    ]
