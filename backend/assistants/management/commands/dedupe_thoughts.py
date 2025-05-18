from django.core.management.base import BaseCommand
from assistants.models import AssistantThoughtLog
from collections import defaultdict


class Command(BaseCommand):
    help = "Removes duplicate AssistantThoughtLogs (same assistant, content, type, and role)"

    def handle(self, *args, **kwargs):
        duplicates_found = 0
        duplicates_deleted = 0

        # Group by a deduplication key
        groups = defaultdict(list)
        for thought in AssistantThoughtLog.objects.all():
            key = (
                str(thought.assistant_id),
                thought.thought.strip(),
                thought.thought_type,
                thought.role,
            )
            groups[key].append(thought)

        for key, entries in groups.items():
            if len(entries) > 1:
                duplicates_found += 1
                # Sort by created_at DESC, keep the first one
                entries.sort(key=lambda t: t.created_at, reverse=True)
                to_delete = entries[1:]
                for dup in to_delete:
                    dup.delete()
                    duplicates_deleted += 1
                    self.stdout.write(f"🗑️ Deleted duplicate: {dup}")

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Done! {duplicates_deleted} duplicates removed from {duplicates_found} sets."
            )
        )
