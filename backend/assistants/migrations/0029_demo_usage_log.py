from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0028_trail_user_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="DemoUsageLog",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("session_id", models.CharField(max_length=64, db_index=True)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("ended_at", models.DateTimeField(null=True, blank=True)),
                ("message_count", models.IntegerField(default=0)),
                ("starter_query", models.TextField(blank=True)),
                ("first_message", models.TextField(blank=True)),
                ("first_message_score", models.FloatField(null=True, blank=True)),
                ("converted_to_real_assistant", models.BooleanField(default=False)),
                ("created_from_ip", models.CharField(max_length=64, blank=True)),
                ("user_agent", models.TextField(blank=True)),
                ("feedback", models.TextField(blank=True)),
                ("assistant", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="demo_logs", to="assistants.assistant")),
            ],
            options={
                "ordering": ["-started_at"],
            },
        ),
    ]
