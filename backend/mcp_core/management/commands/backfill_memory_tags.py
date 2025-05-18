# memory/management/commands/backfill_memory_tags.py

from django.core.management.base import BaseCommand
from memory.models import MemoryEntry
from mcp_core.models import Tag
from embeddings.helpers.helper_tagging import generate_tags_for_memory
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Backfill missing tags on MemoryEntry records using auto-generated tagging."

    def handle(self, *args, **options):
        tagged = 0
        skipped = 0
        failed = 0

        entries = MemoryEntry.objects.filter(tags__isnull=True)
        self.stdout.write(f"🔍 Found {entries.count()} entries with no tags.")

        for memory in entries:
            try:
                tags = generate_tags_for_memory(memory.event)
                if not tags:
                    skipped += 1
                    continue

                tag_objs = []
                for tag in tags:
                    name = tag.strip().lower()
                    slug = slugify(name)
                    obj, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
                    tag_objs.append(obj)

                memory.tags.set(tag_objs)
                tagged += 1
                self.stdout.write(f"🏷️ Tagged memory {memory.id} with: {tags}")

            except Exception as e:
                failed += 1
                self.stderr.write(f"❌ Failed to tag memory {memory.id}: {e}")

        self.stdout.write(self.style.SUCCESS(f"\n✅ Tagging complete!"))
        self.stdout.write(f"✔️ Tagged: {tagged}")
        self.stdout.write(f"⏭️ Skipped: {skipped}")
        self.stdout.write(f"❌ Failed: {failed}")