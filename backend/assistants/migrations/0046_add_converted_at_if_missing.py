from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0045_add_user_rating_if_missing"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE assistants_demousagelog ADD COLUMN IF NOT EXISTS converted_at timestamp with time zone NULL;",
            reverse_sql="ALTER TABLE assistants_demousagelog DROP COLUMN IF EXISTS converted_at;",
        )
    ]
