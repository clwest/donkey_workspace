from django.core.management.base import BaseCommand
from django.utils.text import slugify
from assistants.models import Assistant
from assistants.helpers.memory_helpers import ensure_welcome_memory
from assistants.helpers.logging_helper import reflect_on_birth
from assistants.models.profile import AssistantUserProfile
from assistants.models.reflection import AssistantReflectionLog
from mcp_core.models import MemoryContext, NarrativeThread
from memory.models import MemoryEntry
from assistants.models.assistant import ChatSession


class Command(BaseCommand):
    """Repair assistant boot data and link missing resources."""

    help = "Repair assistants missing boot-time links"

    def handle(self, *args, **options):
        for assistant in Assistant.objects.all():
            changed_fields = []

            if not assistant.memory_context:
                assistant.memory_context = MemoryContext.objects.create(
                    content=f"{assistant.name} context"
                )
                changed_fields.append("memory_context")

            if not assistant.slug:
                assistant.slug = slugify(assistant.name)
                changed_fields.append("slug")

            if not assistant.archetype:
                assistant.archetype = "debugger"
                changed_fields.append("archetype")

            if changed_fields:
                assistant.save(update_fields=changed_fields)

            # Ensure profile with world/archetype defaults
            if assistant.created_by_id:
                profile, _ = AssistantUserProfile.objects.get_or_create(
                    assistant=assistant, user=assistant.created_by
                )
                profile_changed = False
                if not profile.world:
                    profile.world = "core"
                    profile_changed = True
                if not profile.archetype:
                    profile.archetype = assistant.archetype or "debugger"
                    profile_changed = True
                if profile_changed:
                    profile.save()
                    changed_fields.append("profile")

            # Ensure intro memory
            if not MemoryEntry.objects.filter(
                assistant=assistant, type="assistant_intro"
            ).exists():
                ensure_welcome_memory(assistant)
                changed_fields.append("welcome_memory")

            # Ensure at least one reflection
            if not AssistantReflectionLog.objects.filter(assistant=assistant).exists():
                reflect_on_birth(assistant)
                changed_fields.append("origin_reflection")

            # Ensure sessions have a narrative thread
            sessions = ChatSession.objects.filter(
                assistant=assistant, narrative_thread__isnull=True
            )
            if sessions.exists():
                thread = NarrativeThread.objects.create(
                    title=f"{assistant.name} Thread",
                    created_by=assistant.created_by,
                )
                sessions.update(narrative_thread=thread, thread=thread)
                changed_fields.append("narrative_thread")

            if changed_fields:
                self.stdout.write(
                    f"✅ Assistant [{assistant.name}] patched: {', '.join(changed_fields)}"
                )
            else:
                self.stdout.write(f"Assistant [{assistant.name}] already OK")
