import csv
from django.core.management.base import BaseCommand
from assistants.models.demo import DemoUsageLog


class Command(BaseCommand):
    help = "Export demo feedback logs"

    def add_arguments(self, parser):
        parser.add_argument("--format", default="csv")

    def handle(self, *args, **options):
        fmt = options["format"]
        if fmt != "csv":
            self.stderr.write("Only csv format supported")
            return
        writer = csv.writer(self.stdout)
        writer.writerow([
            "session_id",
            "demo_slug",
            "comparison_variant",
            "feedback_text",
            "user_rating",
            "converted_at",
            "created_at",
        ])
        for log in DemoUsageLog.objects.all().order_by("created_at"):
            writer.writerow([
                log.session_id,
                log.demo_slug,
                log.comparison_variant,
                log.feedback_text,
                log.user_rating,
                log.converted_at,
                log.created_at,
            ])
