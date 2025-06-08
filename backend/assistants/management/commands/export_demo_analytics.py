import csv
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from assistants.models.demo import DemoUsageLog
from assistants.models.demo_usage import DemoSessionLog


class Command(BaseCommand):
    help = "Export anonymized demo analytics"

    def add_arguments(self, parser):
        parser.add_argument("--start", type=str, default=None)
        parser.add_argument("--end", type=str, default=None)
        parser.add_argument("--demo_slug", type=str, default=None)
        parser.add_argument("--output", type=str, default=None)

    def handle(self, *args, **options):
        start = parse_date(options.get("start")) if options.get("start") else None
        end = parse_date(options.get("end")) if options.get("end") else None
        demo_slug = options.get("demo_slug")
        output = options.get("output")

        qs = DemoUsageLog.objects.all().order_by("created_at")
        if start:
            qs = qs.filter(created_at__date__gte=start)
        if end:
            qs = qs.filter(created_at__date__lte=end)
        if demo_slug:
            qs = qs.filter(demo_slug=demo_slug)

        target = open(output, "w", newline="") if output else self.stdout
        writer = csv.writer(target)
        writer.writerow([
            "session_id",
            "demo_slug",
            "starter_query",
            "message_count",
            "converted",
            "rating",
            "feedback",
            "interaction_score",
            "likely_to_convert",
            "tips_helpful",
            "created_at",
        ])
        for log in qs:
            session = DemoSessionLog.objects.filter(session_id=log.session_id).first()
            writer.writerow(
                [
                    log.session_id,
                    log.demo_slug,
                    session.starter_query if session else "",
                    session.message_count if session else "",
                    (session.converted_to_real_assistant if session else bool(log.converted_at)),
                    log.user_rating or "",
                    log.feedback_text or (session.feedback if session else ""),
                    session.demo_interaction_score if session else "",
                    session.likely_to_convert if session else "",
                    session.tips_helpful if session else "",
                    log.created_at,
                ]
            )
        if output:
            target.close()

