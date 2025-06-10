from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0047_add_created_at_if_missing"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE assistants_demousagelog ADD COLUMN IF NOT EXISTS started_at timestamp with time zone DEFAULT NOW();",
            reverse_sql="ALTER TABLE assistants_demousagelog DROP COLUMN IF EXISTS started_at;",
        ),
    ]
