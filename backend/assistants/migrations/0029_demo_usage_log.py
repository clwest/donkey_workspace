from django.db import migrations, models

import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):


    dependencies = [
        ("assistants", "0028_trail_user_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="DemoUsageLog",
            fields=[

                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_id", models.CharField(max_length=64, unique=True)),
                (
                    "user",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
                ),
                ("demo_slug", models.CharField(max_length=100)),
                ("comparison_variant", models.CharField(blank=True, max_length=50)),
                ("feedback_text", models.TextField(blank=True)),
                ("user_rating", models.IntegerField(blank=True, null=True)),
                ("converted_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},

        ),
    ]
