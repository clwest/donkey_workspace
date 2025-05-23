from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('agents', '0001_mythchain_models'),
    ]

    operations = [
        migrations.RenameField(
            model_name='symbolicpatternbroadcastengine',
            old_name='broadcast_channel',
            new_name='broadcast_title',
        ),
    ]

