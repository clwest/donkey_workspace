from django.core.management.base import BaseCommand
from assistants.models import Assistant, AssistantReflectionLog
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
import json

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
        AssistantReflectionLog.objects.create(
            assistant=assistant,
            summary=text,
            title="Self Reflection",
            category="self_reflection",
            raw_prompt=prompt,
        )
        if updates:
            if updates.get("persona_summary"):
                assistant.persona_summary = updates["persona_summary"]
            if updates.get("traits"):
                assistant.traits = updates["traits"]
            if updates.get("values") is not None:
                assistant.values = updates["values"]
            if updates.get("motto"):
                assistant.motto = updates["motto"]
            assistant.save()
        self.stdout.write(self.style.SUCCESS("Reflection complete."))
