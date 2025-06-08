import csv
import json
from django.core.management.base import BaseCommand
from assistants.models.demo_usage import DemoSessionLog


class Command(BaseCommand):
    help = "Export DemoSessionLog stats"

    def add_arguments(self, parser):
        parser.add_argument("--as", dest="fmt", default="csv")

    def handle(self, *args, **options):
        fmt = options["fmt"]
        qs = DemoSessionLog.objects.all().order_by("-started_at")
        if fmt == "csv":
            writer = csv.writer(self.stdout)
            writer.writerow([
                "assistant_slug",
                "session_id",
                "started_at",
                "ended_at",
                "message_count",
                "starter_query",
                "converted",
            ])
            for log in qs:
                writer.writerow(
                    [
                        log.assistant.demo_slug or log.assistant.slug,
                        log.session_id,
                        log.started_at,
                        log.ended_at,
                        log.message_count,
                        log.starter_query,
                        log.converted_to_real_assistant,
                    ]
                )
        else:
            data = [
                {
                    "assistant": log.assistant.demo_slug or log.assistant.slug,
                    "session_id": log.session_id,
                    "started_at": log.started_at,
                    "ended_at": log.ended_at,
                    "message_count": log.message_count,
                    "starter_query": log.starter_query,
                    "converted": log.converted_to_real_assistant,
                }
                for log in qs
            ]
            self.stdout.write(json.dumps(data, default=str))
