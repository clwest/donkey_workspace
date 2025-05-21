from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True, blank=True)),
                ('description', models.TextField(blank=True)),
                ('theme', models.CharField(max_length=100, blank=True)),
                ('image_style', models.CharField(max_length=100, blank=True)),
                ('narrator_voice', models.CharField(max_length=100, blank=True, choices=[('Echo', 'Echo'), ('Nova', 'Nova')])),
                ('is_public', models.BooleanField(default=False)),
                ('project_type', models.CharField(max_length=50, choices=[('general', 'General'), ('assistant', 'Assistant'), ('storybook', 'Storybook'), ('gardening', 'Gardening'), ('farming', 'Farming')], default='general')),
                ('goal', models.TextField(blank=True, null=True)),
                ('initial_prompt', models.TextField(blank=True, null=True)),
                ('status', models.CharField(max_length=50, choices=[('active', 'Active'), ('completed', 'Completed'), ('on_hold', 'On Hold'), ('cancelled', 'Cancelled')], default='active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='projects', to='accounts.user')),
                ('participants', models.ManyToManyField(blank=True, related_name='collaborative_projects', through='project.ProjectParticipant', to='accounts.user')),
                ('team', models.ManyToManyField(blank=True, related_name='team_projects', to='assistants.assistant')),
                ('team_chain', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='team_projects', to='assistants.assistantmemorychain')),
                ('assistant', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to='assistants.assistant')),
                ('assistant_project', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='linked_projects', to='assistants.assistantproject')),
                ('narrative_thread', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='narrative_projects', to='mcp_core.narrativethread')),
                ('thread', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='projects', to='mcp_core.narrativethread')),
                ('dev_docs', models.ManyToManyField(blank=True, related_name='projects', to='mcp_core.devdoc')),
                ('created_from_memory', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='spawned_projects', to='memory.memoryentry')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProjectParticipant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=models.CASCADE, related_name='participant_links', to='project.project')),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='project_participations', to='accounts.user')),
            ],
            options={
                'unique_together': {('user', 'project')},
            },
        ),
        migrations.CreateModel(
            name='ProjectTask',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('title', models.CharField(max_length=255)),
                ('notes', models.TextField(blank=True)),
                ('content', models.TextField()),
                ('status', models.CharField(max_length=50, choices=[('todo', 'To Do'), ('in_progress', 'In Progress'), ('done', 'Done')], default='todo')),
                ('priority', models.IntegerField(default=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=models.CASCADE, related_name='core_tasks', to='project.project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectMilestone',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(max_length=50, choices=[('Planned', 'Planned'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], default='Planned')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=models.CASCADE, related_name='milestones', to='project.project')),
            ],
            options={
                'ordering': ['due_date', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProjectMemoryLink',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('reason', models.TextField(blank=True, null=True)),
                ('linked_at', models.DateTimeField(auto_now_add=True)),
                ('memory', models.ForeignKey(on_delete=models.CASCADE, to='memory.memoryentry')),
                ('project', models.ForeignKey(on_delete=models.CASCADE, related_name='linked_memories', to='project.project')),
            ],
            options={
                'ordering': ['-linked_at'],
                'constraints': [
                    models.UniqueConstraint(fields=['project', 'memory'], name='unique_project_memory'),
                ],
            },
        ),
    ]
