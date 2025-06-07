from django.db import migrations, models
import django.db.models.deletion
from django.contrib.postgres.fields import ArrayField

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0024_demo_slug_field"),
    ]

    operations = [
        migrations.RenameField(
            model_name="assistant",
            old_name="spawned_by",
            new_name="spawn_reason",
        ),
        migrations.AddField(
            model_name="assistant",
            name="spawned_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="spawned_children",
                to="assistants.assistant",
            ),
        ),
        migrations.AddField(
            model_name="assistant",
            name="spawned_traits",
            field=ArrayField(
                models.CharField(max_length=20),
                blank=True,
                default=list,
                help_text="Traits inherited from the source assistant",
            ),
        ),
    ]
