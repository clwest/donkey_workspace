# backend/mcp_core/management/commands/reembed_mcp_core.py

from django.core.management.base import BaseCommand
from mcp_core.models import MemoryContext, Plan, Task
from assistants.models import AssistantReflectionLog
from embeddings.helpers.helpers_io import save_embedding


class Command(BaseCommand):
    help = "Re-embed all MemoryContext, Plan, Task, and ReflectionLog records."

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.WARNING("Starting re-embedding of MCP Core models...")
        )

        models = [
            (MemoryContext, "MemoryContext"),
            (Plan, "Plan"),
            (Task, "Task"),
            (AssistantReflectionLog, "AssistantReflectionLog"),
        ]

        total_embeddings = 0

        for model_class, label in models:
            self.stdout.write(self.style.NOTICE(f"Re-embedding {label}..."))

            instances = model_class.objects.all()
            success_count = 0
            fail_count = 0

            for instance in instances:
                try:
                    save_embedding(instance, embedding=[])
                    success_count += 1
                except Exception as e:
                    self.stderr.write(
                        f"Failed to save embedding for {label} ID {instance.id}: {e}"
                    )
                    fail_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"{label}: {success_count} embeddings saved successfully. {fail_count} failures."
                )
            )
            total_embeddings += success_count

        self.stdout.write(
            self.style.SUCCESS(
                f"Re-embedding complete! Total embeddings updated: {total_embeddings}"
            )
        )
