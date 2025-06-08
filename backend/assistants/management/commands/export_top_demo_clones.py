import csv
from django.core.management.base import BaseCommand
from assistants.models import Assistant, ChatSession, AssistantChatMessage


class Command(BaseCommand):
    help = "Export top-performing demo clones"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=10)

    def handle(self, *args, **options):
        limit = options["limit"]
        clones = Assistant.objects.filter(is_demo_clone=True)
        rows = []
        for a in clones:
            sessions = ChatSession.objects.filter(assistant=a)
            count = sessions.count()
            if count == 0:
                continue
            first_msg = (
                AssistantChatMessage.objects.filter(session__assistant=a, role="user")
                .order_by("created_at")
                .first()
            )
            rows.append(
                [
                    a.slug,
                    a.spawned_by.demo_slug if a.spawned_by else "",
                    count,
                    first_msg.content if first_msg else "",
                    a.primary_badge or "",
                ]
            )
        rows.sort(key=lambda r: r[2], reverse=True)
        writer = csv.writer(self.stdout)
        writer.writerow(["slug", "demo_slug", "sessions", "starter_message", "badge"])
        for row in rows[:limit]:
            writer.writerow(row)
