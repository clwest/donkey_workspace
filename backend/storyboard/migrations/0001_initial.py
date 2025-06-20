# Generated by Django 5.2 on 2025-06-12 05:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("assistants", "0003_initial"),
        ("characters", "0003_initial"),
        ("images", "0003_initial"),
        ("mcp_core", "0002_initial"),
        ("memory", "0002_initial"),
        ("story", "0002_initial"),
        ("tts", "0001_initial"),
        ("videos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="NarrativeEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                ("order", models.PositiveIntegerField(default=0)),
                ("scene", models.CharField(blank=True, max_length=100, null=True)),
                ("location_context", models.TextField(blank=True, null=True)),
                ("start_time", models.DateTimeField(blank=True, null=True)),
                ("end_time", models.DateTimeField(blank=True, null=True)),
                ("auto_delegate", models.BooleanField(default=False)),
                ("auto_reflect", models.BooleanField(default=False)),
                ("auto_summarize", models.BooleanField(default=False)),
                ("last_triggered", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "linked_assistant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="linked_narrative_events",
                        to="assistants.assistant",
                    ),
                ),
                (
                    "linked_character",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="narrative_events",
                        to="characters.characterprofile",
                    ),
                ),
                (
                    "linked_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="narrative_events",
                        to="images.image",
                    ),
                ),
                (
                    "linked_memory",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="linked_narrative_events",
                        to="memory.memoryentry",
                    ),
                ),
                (
                    "linked_story",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="narrative_events",
                        to="story.story",
                    ),
                ),
                (
                    "linked_tts",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="narrative_events",
                        to="tts.storyaudio",
                    ),
                ),
                (
                    "linked_video",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="narrative_events",
                        to="videos.video",
                    ),
                ),
                (
                    "narrative_thread",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="events",
                        to="mcp_core.narrativethread",
                    ),
                ),
            ],
            options={
                "ordering": ["order", "created_at"],
            },
        ),
    ]
