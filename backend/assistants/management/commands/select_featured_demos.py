from django.core.management.base import BaseCommand
from assistants.models import Assistant
from assistants.models.demo_usage import DemoSessionLog

class Command(BaseCommand):
    help = "Select top converting demo assistants and mark them as featured"

    def handle(self, *args, **options):
        demos = Assistant.objects.filter(is_demo=True)
        metrics = []
        for demo in demos:
            logs = DemoSessionLog.objects.filter(assistant=demo)
            total = logs.count()
            if not total:
                continue
            conversions = logs.filter(converted_to_real_assistant=True).count()
            rate = conversions / total
            if rate > 0.25:
                metrics.append((demo, rate))
        metrics.sort(key=lambda x: x[1], reverse=True)

        Assistant.objects.filter(is_demo=True).update(is_featured=False, featured_rank=None)
        for idx, (demo, rate) in enumerate(metrics[:3], start=1):
            demo.is_featured = True
            demo.featured_rank = idx
            demo.save(update_fields=["is_featured", "featured_rank"])
            self.stdout.write(f"Featured {demo.name} ({rate:.2%})")
