# mcp_core/management/commands/export_reflections.py

from django.core.management.base import BaseCommand
from mcp_core.models import ReflectionLog
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
        reflections = ReflectionLog.objects.all()
        exported = 0
        export_json = options["json"] or not options["markdown"]
        export_md = options["markdown"] or not options["json"]

        for reflection in reflections:
            filename_slug = slugify(reflection.title or f"reflection-{reflection.id}")
            export_data = {
                "id": reflection.id,
                "title": reflection.title,
                "created_at": reflection.created_at.isoformat(),
                "tags": reflection.tags,
                "mood": reflection.mood,
                "raw_summary": reflection.raw_summary,
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
                    if reflection.tags:
                        f.write(f"**Tags:** {', '.join(reflection.tags)}\n\n")
                    if reflection.mood:
                        f.write(f"**Mood:** {reflection.mood}\n\n")
                    f.write("## Raw Summary\n")
                    f.write(f"```\n{reflection.raw_summary or 'No raw summary.'}\n```\n\n")
                    f.write("## LLM Reflection\n")
                    f.write(f"{reflection.llm_summary or 'No LLM reflection.'}\n")

            exported += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Exported {exported} reflections to {EXPORT_DIR}/")
        )
