from django.core.management.base import BaseCommand

from mcp_core.models import NarrativeThread
from mcp_core.tasks.thread_sync import update_thread_progress

class Command(BaseCommand):
    help = "Sync narrative thread progress from related project milestones"

    def handle(self, *args, **options):
        for thread in NarrativeThread.objects.all():
            update_thread_progress(thread.id)
        self.stdout.write(self.style.SUCCESS("Synced thread progress"))
