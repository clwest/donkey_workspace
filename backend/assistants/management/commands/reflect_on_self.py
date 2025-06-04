from django.core.management.base import BaseCommand
from assistants.models import Assistant, AssistantReflectionLog
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from memory.models import MemoryEntry
import logging
import json

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate a self reflection for an assistant and update identity"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True)

    def handle(self, *args, **options):
        slug = options["assistant"]
        assistant = Assistant.objects.get(slug=slug)
        engine = AssistantReflectionEngine(assistant)
        prompt = (
            f"You are {assistant.name}. Reflect on your recent behavior and suggest"
            " updates to your persona_summary, traits, motto or values if needed."
            " Respond with a short reflection followed by a JSON object of updates."
        )
        output = engine.generate_reflection(prompt)
        text = output
        updates = {}
        if "{" in output:
            try:
                json_part = output[output.index("{") : output.rindex("}") + 1]
                text = output[: output.index("{")].strip()
                updates = json.loads(json_part)
            except Exception:
                pass
        # append reflection scope tag if missing
        if "#reflection-scope" not in text:
            text += "\n#reflection-scope:complete"

        AssistantReflectionLog.objects.create(
            assistant=assistant,
            summary=text,
            title="Self Reflection",
            category="self_reflection",
            raw_prompt=prompt,
        )

        # warn if delegation memories exist but were not covered
        if MemoryEntry.objects.filter(assistant=assistant, type="delegation").exists():
            if "delegation" not in text.lower():
                logger.warning("Delegation memories were not summarized")
        if updates:
            if updates.get("persona_summary"):
                assistant.persona_summary = updates["persona_summary"]
            if updates.get("traits"):
                assistant.traits = updates["traits"]
            if updates.get("personality_description"):
                assistant.personality_description = updates["personality_description"]
            if updates.get("persona_mode"):
                assistant.persona_mode = updates["persona_mode"]
            if updates.get("values") is not None:
                assistant.values = updates["values"]
            if updates.get("motto"):
                assistant.motto = updates["motto"]
            assistant.save()
        self.stdout.write(self.style.SUCCESS("Reflection complete."))
