from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='MythchainOutputGenerator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('generator_name', models.CharField(max_length=150)),
                ('input_payload', models.JSONField(default=dict)),
                ('output_payload', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at'],},
        ),
        migrations.CreateModel(
            name='NarrativeArtifactExporter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('export_format', models.CharField(max_length=50)),
                ('payload', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('generator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='artifact_exports', to='agents.mythchainoutputgenerator')),
            ],
            options={'ordering': ['-created_at'],},
        ),
        migrations.CreateModel(
            name='SymbolicPatternBroadcastEngine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('broadcast_channel', models.CharField(max_length=150)),
                ('pattern_signature', models.CharField(blank=True, max_length=256)),
                ('broadcast_payload', models.JSONField(blank=True, default=dict)),
                ('last_broadcast_at', models.DateTimeField(auto_now=True)),
                ('linked_exporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='broadcast_engines', to='agents.narrativeartifactexporter')),
            ],
            options={'ordering': ['-last_broadcast_at'],},
        ),
    ]
