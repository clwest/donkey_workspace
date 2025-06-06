from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('memory', '0006_rag_playback_extra_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='symbolicmemoryanchor',
            name='acquisition_stage',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('unseen', 'unseen'),
                    ('exposed', 'exposed'),
                    ('acquired', 'acquired'),
                    ('reinforced', 'reinforced'),
                ],
                default='unseen',
            ),
        ),
    ]
