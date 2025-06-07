from django.db import migrations, models

import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('memory', '0008_display_tooltip_location'),
        ('assistants', '0001_initial'),

    ]

    operations = [
        migrations.CreateModel(

            name='GlossaryKeeperLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_taken', models.CharField(max_length=64)),
                ('score_before', models.FloatField(blank=True, null=True)),
                ('score_after', models.FloatField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, default='')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('anchor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keeper_logs', to='memory.symbolicmemoryanchor')),
                ('assistant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='assistants.assistant')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]


