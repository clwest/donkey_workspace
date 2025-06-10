from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("assistants", "0044_auto_start_chat"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE assistants_demousagelog ADD COLUMN IF NOT EXISTS user_rating integer NULL;",
            reverse_sql="ALTER TABLE assistants_demousagelog DROP COLUMN IF EXISTS user_rating;",
        )
    ]
