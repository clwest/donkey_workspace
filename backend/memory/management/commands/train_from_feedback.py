from django.core.management.base import BaseCommand
from django.utils import timezone

from assistants.models import Assistant
from embeddings.helpers.helpers_io import save_embedding
from memory.models import MemoryEntry, MemoryFeedback
from openai import OpenAI
from prompts.models import Prompt, PromptUsageTemplate
from prompts.utils.openai_utils import extract_title_from_prompt


class Command(BaseCommand):
    """Generate system prompts from positively rated feedback."""

    help = "Train system prompts using positive MemoryFeedback entries"

    def handle(self, *args, **options):
        feedback_qs = MemoryFeedback.objects.filter(memory__rating__gt=0)
        if not feedback_qs.exists():
            self.stdout.write(
                self.style.WARNING("No positive feedback found.")
            )
            return

        assistants = (
            feedback_qs.values_list("memory__assistant", flat=True).distinct()
        )
        client = OpenAI()
        for aid in assistants:
            if not aid:
                continue
            assistant = Assistant.objects.filter(id=aid).first()
            if not assistant:
                continue

            mem_ids = (
                feedback_qs.filter(memory__assistant=assistant)
                .values_list("memory_id", flat=True)
            )
            memories = MemoryEntry.objects.filter(id__in=mem_ids)
            if not memories.exists():
                continue

            memory_texts = "\n".join(
                [
                    (
                        f"- {m.event} "
                        f"(Emotion: {m.emotion or 'Neutral'}, "
                        f"Importance: {m.importance}/10)"
                    )
                    for m in memories
                ]
            )

            instruction = (
                "You are a prompt engineer creating a new SYSTEM prompt based "
                "on important personal memories.\n"
                "Write a concise, powerful SYSTEM prompt that guides an "
                "assistant to behave in alignment with the following life "
                "events:\n\n"
                f"{memory_texts}\n\n"
                "The prompt should focus on emotions, lessons learned, and "
                "goals. Make it inspirational but practical."
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": instruction}],
                temperature=0.4,
                max_tokens=1024,
            )
            generated_prompt = response.choices[0].message.content.strip()
            title = extract_title_from_prompt(generated_prompt)
            prompt = Prompt.objects.create(
                title=(
                    title
                    or "System Prompt from Memories "
                    f"{timezone.now().strftime('%Y-%m-%d')}"
                ),
                type="system",
                content=generated_prompt,
                source="feedback-trainer",
                token_count=len(generated_prompt.split()),
                assistant=assistant,
            )
            save_embedding(prompt, embedding=[])
            PromptUsageTemplate.objects.create(
                title=f"Auto: {prompt.title}",
                prompt=prompt,
                agent=assistant,
                trigger_type="on_start",
                role="system",
                priority=0,
            )
            assistant.system_prompt = prompt
            assistant.save(update_fields=["system_prompt"])
            self.stdout.write(
                self.style.SUCCESS(
                    f"Generated prompt for {assistant.slug}: {prompt.slug}"
                )
            )
