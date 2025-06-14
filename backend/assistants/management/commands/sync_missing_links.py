from django.core.management.base import BaseCommand
from django.core.management import call_command
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
from intel_core.models import ChunkTag
from assistants.models.trust import TrustSignalLog

class Command(BaseCommand):
    help = "List assistants missing anchors, context, or trust signals"

    def add_arguments(self, parser):
        parser.add_argument("--fix", action="store_true", help="Attempt to fix missing data")

    def handle(self, *args, **options):
        fix = options.get("fix")
        for a in Assistant.objects.all():
            issues = []
            if not a.memory_context_id:
                issues.append("context")
            if not SymbolicMemoryAnchor.objects.filter(assistant=a).exists():
                issues.append("anchors")
            if not ChunkTag.objects.filter(chunk__document__assistants=a).exists():
                issues.append("chunk_tags")
            if not TrustSignalLog.objects.filter(assistant=a).exists():
                issues.append("trust_signals")
            if issues:
                self.stdout.write(f"{a.slug}: {', '.join(issues)}")
                if fix and "anchors" in issues:
                    call_command("infer_glossary_anchors", "--assistant", a.slug)

