from django.core.management.base import BaseCommand
from agents.models import Agent, AgentLegacy
import random


class Command(BaseCommand):
    help = "Backfill AgentLegacy for existing agents"

    def handle(self, *args, **options):
        for agent in Agent.objects.all():
            legacy, created = AgentLegacy.objects.get_or_create(agent=agent)
            if created:
                legacy.resurrection_count = random.randint(0, 2)
                legacy.missions_completed = random.randint(0, 5)
                legacy.save()
                status = "created"
            else:
                status = "exists"
            self.stdout.write(f"{agent.name} legacy {status}")

        self.stdout.write(self.style.SUCCESS("Agent legacy backfilled."))
