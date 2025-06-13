from django.core.management.base import BaseCommand
from django.db.models import Q
from intel_core.models import (
    DocumentChunk,
    GlossaryMissReflectionLog,
    GlossaryFallbackReflectionLog,
)
from memory.models import SymbolicMemoryAnchor
from assistants.utils.resolve import resolve_assistant
from utils.inspection_helpers import print_glossary_debug_table


class Command(BaseCommand):
    """Inspect glossary chunks associated with a given anchor slug."""

    help = "Inspect glossary chunk linkage for a given anchor slug"

    def add_arguments(self, parser):
        parser.add_argument("--slug", type=str)
        parser.add_argument("--assistant", type=str)
        parser.add_argument(
            "--include-incomplete",
            action="store_true",
            help="Include chunks missing embeddings or scores",
        )

    def handle(self, *args, **options):
        slug = options.get("slug")
        assistant_slug = options.get("assistant")
        include_incomplete = options.get("include_incomplete", False)

        if assistant_slug:
            if not resolve_assistant(assistant_slug):
                self.stdout.write(
                    self.style.ERROR(f"Assistant '{assistant_slug}' not found.")
                )
                return

            anchors = SymbolicMemoryAnchor.objects.filter(
                reinforced_by__slug=assistant_slug
            )
            self.stdout.write(
                f"Total anchors linked to {assistant_slug}: {anchors.count()}"
            )
            if not anchors.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"No anchors linked to assistant '{assistant_slug}'."
                    )
                )
                return

            for anchor in anchors:
                self.stdout.write(
                    f"\n🔎 Anchor {anchor.slug} ({anchor.label})"
                    f" source={anchor.source} created={anchor.created_at.date()}"
                )
                chunks = (
                    DocumentChunk.objects.filter(
                        Q(anchor=anchor) | Q(matched_anchors__contains=[anchor.slug])
                    )
                    .select_related("document")
                    .order_by("order")
                )
                if not include_incomplete:
                    chunks = chunks.exclude(embedding__isnull=True).exclude(
                        score__isnull=True
                    )

                print_glossary_debug_table(self.stdout, anchor.slug, chunks)
                if chunks.count() == 0:
                    self.stdout.write("⚠️ No chunk matches for this anchor")
                direct = chunks.filter(anchor=anchor).count()
                retagged = chunks.exclude(anchor=anchor).count()
                self.stdout.write(f"Matched direct: {direct} | retagged: {retagged}")
                unresolved = GlossaryMissReflectionLog.objects.filter(
                    anchor=anchor, reflection__isnull=True
                ).count()
                fallback = GlossaryFallbackReflectionLog.objects.filter(
                    anchor_slug=anchor.slug
                ).count()
                self.stdout.write(f"Unresolved miss logs: {unresolved}")
                self.stdout.write(f"Fallback logs: {fallback}")
            return

        if not slug:
            self.stdout.write(self.style.ERROR("Provide either --slug or --assistant"))
            return

        try:
            anchor = SymbolicMemoryAnchor.objects.get(slug=slug)
        except SymbolicMemoryAnchor.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Anchor '{slug}' not found."))
            return

        chunks = (
            DocumentChunk.objects.filter(anchor=anchor)
            .select_related("document")
            .order_by("order")
        )
        if not include_incomplete:
            chunks = chunks.exclude(embedding__isnull=True).exclude(score__isnull=True)

        self.stdout.write(
            f"Anchor {anchor.slug} ({anchor.label}) source={anchor.source} created={anchor.created_at.date()}"
        )
        print_glossary_debug_table(self.stdout, slug, chunks)
        if chunks.count() == 0:
            self.stdout.write("⚠️ No chunk matches for this anchor")
