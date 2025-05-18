import os
import frontmatter
from django.conf import settings
from django.core.management.base import BaseCommand
from prompts.models import Prompt


class Command(BaseCommand):
    help = "Ingest markdown prompt files from a directory into the Prompt model"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-dir",
            type=str,
            default=None,
            help="Root folder containing subdirs of prompt markdown files",
        )

    def handle(self, *args, **options):
        root = options["source_dir"] or getattr(settings, "PROMPTS_ROOT", None)
        if not root or not os.path.isdir(root):
            self.stderr.write(
                self.style.ERROR(
                    "Please set settings.PROMPTS_ROOT or pass --source-dir pointing to your prompt folders."
                )
            )
            return

        # Walk each subdirectory (e.g. "Anthropic")
        for source in os.listdir(root):
            source_path = os.path.join(root, source)
            if not os.path.isdir(source_path):
                continue

            # Find all .md files
            for fname in os.listdir(source_path):
                if not fname.lower().endswith(".md"):
                    continue

                file_path = os.path.join(source_path, fname)
                post = frontmatter.load(file_path)
                # Title from frontmatter or filename without extension
                title = post.get("title") or os.path.splitext(fname)[0]
                # Prompt type from frontmatter or default to 'system'
                prompt_type = post.get("type", "system")
                content = post.content.strip()

                obj, created = Prompt.objects.update_or_create(
                    source=source,
                    title=title,
                    defaults={
                        "type": prompt_type,
                        "content": content,
                    },
                )
                status = "Created" if created else "Updated"
                self.stdout.write(f"{status} prompt '{title}' (source={source})")
