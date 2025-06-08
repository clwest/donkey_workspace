import csv
from io import StringIO
from assistants.models.demo_usage import DemoSessionLog


def export_demo_usage_csv():
    """Return demo usage log as CSV string."""
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
    for log in DemoSessionLog.objects.all().order_by("-started_at"):
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
