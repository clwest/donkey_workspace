from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('assistants', '0001_initial'),
        ('agents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerformanceMetric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('value', models.FloatField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('assistant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistants.assistant')),
            ],
        ),
        migrations.CreateModel(
            name='RitualPerformanceMetric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbolic_score', models.FloatField()),
                ('transformation_alignment', models.FloatField()),
                ('mythic_tags', models.JSONField()),
                ('reflection_notes', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assistant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistants.assistant')),
                ('ritual', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agents.ritualarchiveentry')),
            ],
        ),
    ]
