from django.core.management.base import BaseCommand
from assistants.models import Assistant, DemoUsageLog


class Command(BaseCommand):
    help = "List demo assistants with high conversions but low feedback rates"

    def add_arguments(self, parser):
        parser.add_argument("--min", type=int, default=5, help="Minimum conversions")
        parser.add_argument(
            "--threshold", type=float, default=0.3, help="Minimum feedback rate"
        )

    def handle(self, *args, **options):
        minimum = options["min"]
        threshold = options["threshold"]
        demos = Assistant.objects.filter(is_demo=True)
        for demo in demos:
            logs = DemoUsageLog.objects.filter(demo_slug=demo.demo_slug)
            conv = logs.filter(converted_at__isnull=False).count()
            feedback = logs.filter(feedback_submitted=True).count()
            if conv >= minimum:
                rate = feedback / conv if conv else 0
                if rate < threshold:
                    self.stdout.write(
                        f"{demo.demo_slug}: {conv} conversions, {rate:.0%} feedback"
                    )
