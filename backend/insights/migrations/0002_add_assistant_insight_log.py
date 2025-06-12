from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [
        ('insights', '0001_initial'),
        ('assistants', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssistantInsightLog',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tags', models.JSONField(default=list, blank=True)),
                ('summary', models.TextField()),
                ('proposed_prompt', models.TextField(null=True, blank=True)),
                ('accepted', models.BooleanField(default=False)),
                ('assistant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='insight_logs', to='assistants.assistant')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assistant_insights', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
