import logging
from openai import OpenAI
from assistants.models import (
    AssistantReflectionLog,
    Assistant,
    AssistantProject,
    AssistantReflectionInsight,
)
from mcp_core.models import MemoryContext, DevDoc
from intel_core.models import Document
from memory.models import MemoryEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from assistants.models import AssistantProject

logger = logging.getLogger(__name__)
client = OpenAI()


class AssistantReflectionEngine:
    def __init__(self, assistant):
        self.assistant = assistant
        self.project = self.get_or_create_project(assistant)

    def build_reflection_prompt(self, memories: list[str]) -> str:
        joined_memories = "\n".join(memories)
        return f"""You are {self.assistant.name}, an AI assistant with reflective capabilities.

    Below are some recent memory entries. Reflect on them and identify key patterns, changes in behavior, emerging goals, or important facts.

    Use 3–6 thoughtful bullet points to summarize your reflections.

    Memories:
    \"\"\"
    {joined_memories}
    \"\"\"
    """

    def generate_reflection(self, prompt: str, temperature: float = 0.5) -> str:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()

    def reflect_now(self, context: MemoryContext) -> str:
        entries = MemoryEntry.objects.filter(context=context).order_by("-created_at")[
            :30
        ]
        texts = [e.event.strip() for e in entries if e.event.strip()]

        if not texts:
            logger.warning("[🧠] No recent memory content to reflect on.")
            return "No meaningful content."

        prompt = self.build_reflection_prompt(texts)

        try:
            reflection = self.generate_reflection(prompt)
            AssistantReflectionLog.objects.create(
                assistant=self.assistant,
                context=context,
                summary=reflection,
                raw_prompt=prompt,
            )
            MemoryEntry.objects.create(
                event=reflection,
                assistant=self.assistant,
                source_role="assistant",
                linked_content_type=ContentType.objects.get_for_model(self.assistant),
                linked_object_id=self.assistant.id,
                is_conversation=False,
                related_project=context.project if context.project else None,
            )
            logger.info(f"[🧠] Reflection saved for context {context.id}.")
            return reflection
        except Exception as e:
            logger.error(f"[❌] Reflection failed: {e}", exc_info=True)
            return "Reflection failed."
    
    @staticmethod
    def get_reflection_assistant():
        slug = slugify("Reflection Engine")
        assistant, created = Assistant.objects.get_or_create(
            slug=slug,
            defaults={
                "name": "Reflection Engine",
                "description": "Analyzes DevDocs and reflects on system evolution.",
                "specialty": "assistant_reflection",
                "tone": "analytical",
                "preferred_model": "gpt-4o",
            },
        )
        if created:
            print(f"✅ Created Assistant: {assistant.name}")
        return assistant

    @staticmethod
    def get_or_create_project(assistant):
        project, _ = AssistantProject.objects.get_or_create(
            assistant=assistant,
            defaults={
                "title": "System Reflection",
                "description": "Ongoing reflections on code and architecture evolution.",
            },
        )
        return project
    

    def reflect_on_document(self, document):
        """Reflect on a Document or DevDoc instance and save insights."""

        # Allow passing a DevDoc; use its linked Document
        if isinstance(document, DevDoc):
            if not document.linked_document:
                raise ValueError(f"DevDoc '{document.title}' has no linked Document")
            target_document = document.linked_document
        else:
            target_document = document

        logger.info(
            f"[ReflectionEngine] Reflecting on document: {target_document.title}"
        )
        
        # Placeholder reflection logic (replace with your actual logic)
        summary = f"Auto-generated summary for {target_document.title}"
        insights = [
            f"Insight 1 about {target_document.title}",
            f"Insight 2 about {target_document.title}",
        ]

        # Save insights
        for insight in insights:
            AssistantReflectionInsight.objects.create(
                assistant=self.assistant,
                linked_document=target_document,
                text=insight,
            )

        return summary, insights
    
    def reflect_on_memory(self, memory: MemoryEntry):
        """
        Create a reflection log for a single memory entry.
        """
        if not memory or not memory.event.strip():
            return None

        prompt = f"""You are {self.assistant.name}, an AI assistant with reflective capabilities.

    Below is a memory entry.

    Reflect on it and summarize the insight in 2–4 thoughtful bullet points.

    Memory:
    \"\"\"
    {memory.event.strip()}
    \"\"\""""

        try:
            reflection = self.generate_reflection(prompt)

            AssistantReflectionLog.objects.create(
                project=self.project,
                assistant=self.assistant,
                linked_memory=memory,
                title=f"Reflection on memory {memory.id}",
                summary=reflection,
                raw_prompt=prompt,
                category="meta"
            )

            logger.info(f"[✅] Reflection log created for memory {memory.id}")
            return reflection
        except Exception as e:
            logger.error(f"[❌] Failed to reflect on memory {memory.id}: {e}", exc_info=True)
            return None
    def reflect_on_assistant(self, assistant: Assistant, project: AssistantProject) -> str:
        """Generate a reflection about a newly spawned assistant."""
        prompt = f"""You are {self.assistant.name}, reflecting on a delegated assistant you created.\n\n" \
                f"Assistant Name: {assistant.name}\n" \
                f"Specialty: {assistant.specialty or '(unspecified)'}\n" \
                f"Description: {assistant.description or '(none)'}\n" \
                "Provide constructive feedback on its purpose, tone, and any improvements."""
        return self.generate_reflection(prompt)
