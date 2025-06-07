from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):
    dependencies = [
        ('memory', '0009_glossary_keeper_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='symbolicmemoryanchor',
            name='is_stable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='symbolicmemoryanchor',
            name='stabilized_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='symbolicmemoryanchor',
            name='drift_priority_score',
            field=models.FloatField(default=0.0),
        ),
    ]
