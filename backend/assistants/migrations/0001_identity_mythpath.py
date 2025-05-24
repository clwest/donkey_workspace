from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='IdentityAnchor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codex_vector', models.JSONField(blank=True, default=dict)),
                ('memory_origin', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assistant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='identity_anchor', to='assistants.assistant')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='TemporalMythpathRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('events', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assistant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mythpath_record', to='assistants.assistant')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='MythpathEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('codex_source', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assistant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mythpath_events', to='assistants.assistant')),
            ],
            options={'ordering': ['created_at']},
        ),
        migrations.CreateModel(
            name='MythpathSerializationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exported_data', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assistant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistants.assistant')),
                ('record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistants.temporalmythpathrecord')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
