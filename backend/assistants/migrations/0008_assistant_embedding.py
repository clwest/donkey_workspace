from django.db import migrations
from pgvector.django import VectorField


class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0007_auto_placeholder"),
    ]

    operations = [
        migrations.AddField(
            model_name="assistant",
            name="embedding",
            field=VectorField(dimensions=1536, null=True, blank=True),
        ),
    ]
