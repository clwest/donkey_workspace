from django.core.management.base import BaseCommand
from embeddings.management.commands.fix_embedding_content import Command as FixContent
from embeddings.management.commands.repair_embedding_links import Command as FixLinks
from embeddings.management.commands.repair_flagged_embeddings import (
    Command as FixFlagged,
)
from memory.management.commands.repair_context_embeddings import Command as FixContext


class Command(BaseCommand):
    help = "Run all embedding repair tasks in order"

    def add_arguments(self, parser):
        parser.add_argument(
            "--assistant", help="Assistant slug or id for context repairs"
        )

    def handle(self, *args, **options):
        assistant = options.get("assistant")
        self.stdout.write("⚙ Running fix_embedding_content")
        FixContent().handle(limit=None)
        self.stdout.write("⚙ Running repair_embedding_links")
        FixLinks().handle(limit=None)
        self.stdout.write("⚙ Running repair_flagged_embeddings")
        FixFlagged().handle()
        if assistant:
            self.stdout.write("⚙ Running repair_context_embeddings")
            FixContext().handle(assistant=assistant)
        self.stdout.write(self.style.SUCCESS("✓ Embedding repair complete"))
