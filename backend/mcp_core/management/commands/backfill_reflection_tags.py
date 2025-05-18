# memory/management/commands/backfill_reflection_tags.py

from django.core.management.base import BaseCommand
from memory.models import MemoryEntry
from mcp_core.models import Tag
from embeddings.helpers.helper_tagging import generate_tags_for_memory
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Backfill tags on MemoryEntry records of type 'reflection' that are missing tags."

    def handle(self, *args, **options):
        reflections = MemoryEntry.objects.filter(type="reflection", tags__isnull=True)
        self.stdout.write(f"🔍 Found {reflections.count()} reflection entries without tags.")

        tagged = 0
        skipped = 0
        failed = 0

        for memory in reflections:
            try:
                tags = generate_tags_for_memory(memory.event)
                if not tags:
                    skipped += 1
                    continue

                tag_objs = []
                for tag in tags:
                    name = tag.lower().strip()
                    slug = slugify(name)
                    tag_obj, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
                    tag_objs.append(tag_obj)

                memory.tags.set(tag_objs)
                tagged += 1
                self.stdout.write(f"🧠 Tagged reflection {memory.id}: {tags}")

            except Exception as e:
                failed += 1
                self.stderr.write(f"❌ Error tagging {memory.id}: {e}")

        self.stdout.write(self.style.SUCCESS("\n✅ Reflection tagging complete."))
        self.stdout.write(f"✔️ Tagged: {tagged}")
        self.stdout.write(f"⏭️ Skipped: {skipped}")
        self.stdout.write(f"❌ Failed: {failed}")