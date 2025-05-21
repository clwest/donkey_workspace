from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='NarrativeEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('scene', models.CharField(max_length=100, blank=True, null=True)),
                ('location_context', models.TextField(blank=True, null=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('auto_delegate', models.BooleanField(default=False)),
                ('auto_reflect', models.BooleanField(default=False)),
                ('auto_summarize', models.BooleanField(default=False)),
                ('last_triggered', models.DateTimeField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['order', 'created_at']},
        ),
    ]
