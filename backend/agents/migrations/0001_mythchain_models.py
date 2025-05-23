from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MythchainOutputGenerator",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("assistant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="assistants.assistant")),
                ("output_title", models.CharField(max_length=150)),
                ("codex_alignment_map", models.JSONField()),
                ("symbolic_summary", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("seed_memory", models.ManyToManyField(to="agents.SwarmMemoryEntry")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="NarrativeArtifactExporter",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("artifact_title", models.CharField(max_length=150)),
                ("export_format", models.CharField(max_length=10)),
                ("auto_compress", models.BooleanField(default=False)),
                ("symbolic_footer", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "assistant",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="assistants.assistant"),
                ),
                (
                    "source_story",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="story.story"),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="SymbolicPatternBroadcastEngine",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("broadcast_title", models.CharField(max_length=150)),
                ("symbolic_payload", models.JSONField()),
                ("belief_waveform_data", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "source_guild",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="assistants.codexlinkedguild"),
                ),
                (
                    "target_assistants",
                    models.ManyToManyField(to="assistants.Assistant"),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
