# mcp_core/management/commands/export_reflections.py

from django.core.management.base import BaseCommand
from assistants.models.reflection import AssistantReflectionLog
import os
import json
from django.utils.text import slugify

EXPORT_DIR = "exports/reflections"


class Command(BaseCommand):
    help = "Export all reflections to Markdown and JSON files."

    def add_arguments(self, parser):
        parser.add_argument("--json", action="store_true", help="Export JSON only")
        parser.add_argument(
            "--markdown", action="store_true", help="Export Markdown only"
        )

    def handle(self, *args, **options):
        os.makedirs(EXPORT_DIR, exist_ok=True)
        reflections = AssistantReflectionLog.objects.all().prefetch_related("tags")
        exported = 0
        export_json = options["json"] or not options["markdown"]
        export_md = options["markdown"] or not options["json"]

        for reflection in reflections:
            filename_slug = slugify(reflection.title or f"reflection-{reflection.id}")
            tag_slugs = list(reflection.tags.values_list("slug", flat=True))
            export_data = {
                "id": str(reflection.id),
                "title": reflection.title,
                "created_at": reflection.created_at.isoformat(),
                "tags": tag_slugs,
                "mood": reflection.mood,
                # `AssistantReflectionLog` stores the raw text in `raw_prompt`.
                # Older code referenced `raw_summary`, so export both keys for
                # compatibility if present.
                "raw_prompt": getattr(reflection, "raw_prompt", ""),
                "summary": reflection.summary,
                "llm_summary": reflection.llm_summary,
            }

            if export_json:
                json_path = os.path.join(EXPORT_DIR, f"{filename_slug}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

            if export_md:
                md_path = os.path.join(EXPORT_DIR, f"{filename_slug}.md")
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(f"# 🧠 {reflection.title}\n\n")
                    f.write(
                        f"**Created At:** {reflection.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                    )
                    if tag_slugs:
                        f.write(f"**Tags:** {', '.join(tag_slugs)}\n\n")
                    if reflection.mood:
                        f.write(f"**Mood:** {reflection.mood}\n\n")
                    f.write("## Raw Prompt\n")
                    raw_text = getattr(reflection, "raw_prompt", "")
                    f.write(f"```\n{raw_text or 'No raw prompt.'}\n```\n\n")
                    f.write("## LLM Reflection\n")
                    f.write(f"{reflection.llm_summary or 'No LLM reflection.'}\n")

            exported += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Exported {exported} reflections to {EXPORT_DIR}/")
        )
