from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ("assistants", "0029_demo_usage_log"),
    ]

    operations = [
        migrations.CreateModel(
            name="DemoSessionLog",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("assistant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="demo_logs", to="assistants.assistant")),
                ("session_id", models.CharField(max_length=64, db_index=True)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("message_count", models.IntegerField(default=0)),
                ("starter_query", models.TextField(blank=True)),
                ("first_message", models.TextField(blank=True)),
                ("first_message_score", models.FloatField(blank=True, null=True)),
                ("converted_to_real_assistant", models.BooleanField(default=False)),
                ("created_from_ip", models.CharField(blank=True, max_length=64)),
                ("user_agent", models.TextField(blank=True)),
                ("feedback", models.TextField(blank=True)),
            ],
            options={"ordering": ["-started_at"]},
        ),
    ]
