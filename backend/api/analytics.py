import csv
from io import StringIO
from assistants.models.demo_usage import DemoUsageLog


def export_demo_usage_csv(start_date=None, demo_slug=None, converted_only=False):
    """Return demo usage log as CSV string."""
    qs = DemoUsageLog.objects.all().order_by("-started_at")
    if start_date:
        qs = qs.filter(started_at__gte=start_date)
    if demo_slug:
        qs = qs.filter(assistant__demo_slug=demo_slug)
    if converted_only:
        qs = qs.filter(converted_to_real_assistant=True)

    out = StringIO()
    writer = csv.writer(out)
    writer.writerow(
        [
            "assistant_slug",
            "session_id",
            "started_at",
            "ended_at",
            "message_count",
            "converted",
        ]
    )
    for log in qs:
        writer.writerow(
            [
                log.assistant.demo_slug or log.assistant.slug,
                log.session_id,
                log.started_at,
                log.ended_at,
                log.message_count,
                log.converted_to_real_assistant,
            ]
        )
    return out.getvalue()
