from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=20, default='queued', choices=[('queued','Queued'),('generating','Generating'),('completed','Completed'),('failed','Failed')])),
                ('title', models.CharField(max_length=200, blank=True)),
                ('prompt', models.TextField()),
                ('summary', models.TextField(blank=True, null=True)),
                ('generated_text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cover_image_url', models.URLField(blank=True, null=True)),
                ('theme', models.CharField(max_length=100, blank=True, null=True)),
                ('tags', models.JSONField(default=list, blank=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('is_reward', models.BooleanField(default=False)),
                ('reward_reason', models.CharField(max_length=255, blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image_caption', models.TextField(blank=True, null=True)),
                ('image_alt_text', models.CharField(max_length=300, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LoreEntry',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('tone', models.CharField(max_length=50, default='mystic')),
                ('epithets', models.JSONField(default=list, blank=True)),
                ('traits', models.JSONField(default=list, blank=True)),
                ('lineage', models.CharField(max_length=100, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='NarrativeEvent',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('scene_summary', models.TextField(blank=True, null=True)),
                ('summary_generated', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
