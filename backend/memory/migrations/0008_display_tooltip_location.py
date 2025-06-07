from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('memory', '0007_anchor_acquisition'),
    ]

    operations = [
        migrations.AddField(
            model_name='symbolicmemoryanchor',
            name='display_tooltip',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='symbolicmemoryanchor',
            name='display_location',
            field=models.JSONField(default=list, blank=True),
        ),
    ]
