from django.db import migrations, models
import project.models

class Migration(migrations.Migration):

    dependencies = [
        ("project", "0002_project_roles_project_team_project_team_chain"),
    ]

    operations = [
        migrations.AddField(
            model_name='projectmilestone',
            name='status',
            field=models.CharField(max_length=50, choices=project.models.MilestoneStatus.choices, default=project.models.MilestoneStatus.PLANNED),
        ),
    ]
