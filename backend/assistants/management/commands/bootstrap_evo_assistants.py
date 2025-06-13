from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from pathlib import Path

from assistants.models import Assistant
from assistants.utils.resolve import resolve_assistant
from intel_core.services.document_service import DocumentService


class Command(BaseCommand):
    help = (
        "Bootstrap assistants from evolutionary AI whitepapers located in"
        " /media/temp"
    )

    ASSISTANTS = [
        {
            "filename": "DGM-WhitePaper.pdf",
            "slug": "godelbot",
            "name": "GödelBot",
            "archetype": "Self-Evolving Architect",
        },
        {
            "filename": "AlphaEvolve Whitepaper.pdf",
            "slug": "evolancer",
            "name": "EvoLancer",
            "archetype": "Competitive Strategist",
        },
        {
            "filename": "Apple-Whitepaper.pdf",
            "slug": "ghost-of-steve",
            "name": "Ghost of Steve",
            "archetype": "Skeptical Memory Oracle",
        },
    ]

    def handle(self, *args, **options):
        media_root = getattr(settings, "MEDIA_ROOT", Path("media"))
        temp_dir = Path(media_root) / "temp"
        created = 0
        for entry in self.ASSISTANTS:
            pdf_path = temp_dir / entry["filename"]
            if not pdf_path.exists():
                self.stderr.write(f"Missing file: {pdf_path}")
                continue

            assistant = resolve_assistant(entry["slug"])
            new = False
            if not assistant:
                assistant, new = Assistant.objects.get_or_create(
                    slug=entry["slug"],
                    defaults={
                        "name": entry["name"],
                        "specialty": entry["archetype"],
                        "archetype": entry["archetype"],
                        "tone_profile": "neutral",
                    },
                )
            if new:
                created += 1
                msg = self.style.SUCCESS(f"Created assistant {assistant.slug}")
                self.stdout.write(msg)

            with open(pdf_path, "rb") as f:
                ingest_info = DocumentService.ingest(
                    source_type="pdf",
                    files=[f],
                    title=entry["name"],
                    assistant_id=str(assistant.id),
                )
            doc_ids = [
                i.get("document_id")
                for i in ingest_info
                if i.get("document_id")
            ]
            if doc_ids:
                for doc_id in doc_ids:
                    call_command(
                        "reflect_on_document",
                        "--doc",
                        str(doc_id),
                        "--assistant",
                        assistant.slug,
                    )
                assistant.assigned_documents.add(*doc_ids)
                call_command(
                    "infer_glossary_anchors",
                    "--assistant",
                    assistant.slug,
                )

        total = len(self.ASSISTANTS)
        self.stdout.write(self.style.SUCCESS(f"Processed {total} whitepapers"))
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created {created} new assistants")
            )
