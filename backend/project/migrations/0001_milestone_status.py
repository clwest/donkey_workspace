from django.db import migrations, models
import project.models

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.AddField(
            model_name='projectmilestone',
            name='status',
            field=models.CharField(max_length=50, choices=project.models.MilestoneStatus.choices, default=project.models.MilestoneStatus.PLANNED),
        ),
    ]
