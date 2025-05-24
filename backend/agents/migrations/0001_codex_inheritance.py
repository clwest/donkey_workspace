from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CodexInheritanceLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inherited_clauses', models.JSONField(blank=True, default=list)),
                ('mutated_clauses', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='codex_parents', to='assistants.assistant')),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='codex_children', to='assistants.assistant')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='CodexLineageThread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lineage_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assistant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistants.assistant')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
