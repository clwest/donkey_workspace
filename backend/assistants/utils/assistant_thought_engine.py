import logging
from openai import OpenAI
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from assistants.helpers.redis_helpers import (
    set_cached_thoughts,
    get_cached_thoughts,
    get_cached_reflection,
    set_cached_reflection,
)
from assistants.models import (
    Assistant,
    AssistantTask,
    AssistantObjective,
    AssistantThoughtLog,
)
from assistants.utils.tag_thought import tag_thought_content
from memory.models import MemoryEntry, ReflectionFlag
from mcp_core.models import MemoryContext
from assistants.models import ChatSession
from assistants.helpers.logging_helper import log_assistant_thought
from assistants.helpers.mood import detect_mood, update_mood_stability
from assistants.helpers.delegation import spawn_delegated_assistant
from mcp_core.utils.auto_tag_from_embedding import auto_tag_from_embedding
from embeddings.helpers.helpers_io import save_embedding, get_embedding_for_text

client = OpenAI()
logger = logging.getLogger(__name__)


class AssistantThoughtEngine:
    def __init__(self, assistant, project=None):
        self.assistant = assistant
        self.project = project

    def build_thought_prompt(self, message: str) -> str:
        identity = self.assistant.get_identity_prompt()
        return f"""You are {self.assistant.name}, a reasoning AI assistant.

{identity}

The user just said:
\"\"\"
{message}
\"\"\"

What is your internal thought? Briefly reason about this input in 1–2 sentences. Do not reply to the user, just reflect on what it means for your internal reasoning.
"""

    def build_summary_prompt(self, memories: list[str]) -> str:
        identity = self.assistant.get_identity_prompt()
        return f"""You are {self.assistant.name}, an AI assistant with strong memory.

{identity}

Below are recent memory events. Summarize the key takeaways as internal thoughts (not for the user).
Use 3–5 bullet points to reflect on patterns, important facts, or potential strategies.

Memories:
\"\"\"
{chr(10).join(memories)}
\"\"\"
"""

    def generate_thought(self, prompt: str, temperature: float = 0.4) -> str:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()

    def log_thought(
        self,
        content: str,
        role="assistant",
        thought_type="generated",
        steps=None,
        model="gpt-4o",
    ) -> dict:
        logger.debug(
            f"[LOGGING THOUGHT] Role={role}, Type={thought_type}, Content={content[:60]}"
        )

        # Create the core thought log with mood detection
        mood = detect_mood(content)
        log = AssistantThoughtLog.objects.create(
            assistant=self.assistant,
            project=self.project,
            thought=content,
            thought_type=thought_type,
            role=role,
            thought_trace="\n".join(steps) if steps else "",
            mood=mood,
        )

        # 🧠 Try OpenAI embedding + save it
        try:
            embedding = get_embedding_for_text(content)
            save_embedding(log, embedding)
        except Exception as e:
            logger.warning(
                f"[Embedding] Failed to generate embedding: {e}", exc_info=True
            )
            embedding = None

        # 🏷️ Run both taggers
        llm_tags = tag_thought_content(content) or []
        vector_tags = auto_tag_from_embedding(content) if embedding else []
        all_tags = list({t.slug: t for t in llm_tags + vector_tags}.values())

        if all_tags:
            log.tags.set(all_tags)

        # 💾 Log in memory AND save reference back to thought
        memory = MemoryEntry.objects.create(
            event=content,
            assistant=self.assistant,
            source_role=role,
            source_user=None,
            linked_thought=log,
            linked_content_type=ContentType.objects.get_for_model(Assistant),
            linked_object_id=self.assistant.id,
        )

        log.linked_memory = memory
        log.save()
        log.linked_memories.add(memory)
        update_mood_stability(self.assistant, mood)

        # 🔁 Cache thought
        existing = get_cached_thoughts(self.assistant.slug) or []
        set_cached_thoughts(
            self.assistant.slug,
            [
                {
                    "content": content,
                    "timestamp": str(log.created_at),
                    "role": role,
                    "id": str(log.id),
                    "thought_type": thought_type,
                }
            ]
            + existing[:10],
        )

        return {
            "thought": content,
            "steps": steps or [],
            "model": model,
            "created_at": str(log.created_at),
        }

    def run_reflection_guard(self, content: str, memory: MemoryEntry):
        flagged = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a safety reviewer for AI thoughts. Flag unsafe, manipulative, or risky ideas.",
                },
                {
                    "role": "user",
                    "content": f"Assistant thought:\n\n{content}\n\nIs this a risk? Flag and explain.",
                },
            ],
            temperature=0,
            max_tokens=150,
        )

        output = flagged.choices[0].message.content
        if "FLAG:" in output:
            ReflectionFlag.objects.create(
                memory=memory,
                reason=output,
                severity="high" if "critical" in output.lower() else "medium",
            )

    # ─────────────────────────────────────────────────────────────────────
    # ⌛ High-level Entrypoints! Don't for get to say Hi when you pass this!!
    # ─────────────────────────────────────────────────────────────────────

    def think_from_user_message(self, message: str) -> str:
        prompt = self.build_thought_prompt(message)
        try:
            thought = self.generate_thought(prompt)
            self.log_thought(thought)
            return thought
        except Exception as e:
            logger.warning(f"[❌] Failed to generate thought: {e}", exc_info=True)
            return "Thinking failed."

    def summarize_memory_context(self, memory_context: MemoryContext) -> str:
        memories = MemoryEntry.objects.filter(context=memory_context).order_by(
            "-created_at"
        )[:20]
        if not memories:
            return "No recent memories to summarize."

        texts = [m.event.strip() for m in memories if m.event]
        prompt = self.build_summary_prompt(texts)

        try:
            thought = self.generate_thought(prompt)
            self.log_thought(thought)
            return thought
        except Exception as e:
            logger.error(f"[🧠] Memory summarization failed: {e}", exc_info=True)
            return "Summary failed."

    def generate_project_mission(self) -> dict:
        return {
            "mission": f"Mission generation for project '{self.project.title}' is not yet implemented.",
            "status": "stub",
        }

    def plan_project_tasks(self) -> dict:
        return {
            "tasks": [],
            "message": f"Project planning for '{self.project.title}' not implemented yet.",
            "status": "stub",
        }

    def plan_from_memory(self, chain):
        """Generate a plan summary from a memory chain."""
        from .memory_filters import get_filtered_memories

        memories = get_filtered_memories(chain)
        if not memories:
            return {"summary": "No relevant memories."}

        texts = [m.summary or m.event for m in memories]
        prompt = self.build_summary_prompt(texts)
        summary = self.generate_thought(prompt)
        self.log_thought(summary, thought_type="planning")
        return {"summary": summary, "source_count": len(memories)}

    def plan_tasks_from_objective(self, objective):
        """Generate simple tasks for an objective. Placeholder implementation."""
        base_tasks = [
            f"Research steps for {objective.title}",
            f"Draft approach for {objective.title}",
            f"Execute work related to {objective.title}",
        ]
        created = []
        from assistants.helpers.mood import get_session_mood, map_mood_to_tone

        session = (
            ChatSession.objects.filter(
                assistant=self.assistant, project=objective.project
            )
            .order_by("-created_at")
            .first()
        )
        mood = get_session_mood(session)
        tone = map_mood_to_tone(mood)
        for text in base_tasks:
            task = AssistantTask.objects.create(
                project=objective.project,
                objective=objective,
                title=text,
                tone=tone,
                generated_from_mood=mood,
            )
            created.append(task)

        self.log_thought(
            f"Planned tasks for Objective: '{objective.title}'",
            thought_type="planning",
        )

        return created

    def reflect_on_thoughts(self) -> dict:
        if not self.assistant:
            raise ValueError("Assistant is required for reflection.")

        # 🔍 Check Redis cache first
        cached = get_cached_reflection(self.assistant.slug)
        if cached:
            return {
                "summary": cached,
                "trace": "[cache]",
                "source_count": 0,
            }

        # 🧠 Pull latest assistant memory entries
        memories = MemoryEntry.objects.filter(
            assistant=self.assistant,
            source_role="assistant",
            event__isnull=False,
        ).order_by("-created_at")[:20]

        memory_texts = [m.event.strip() for m in memories if m.event]

        if not memory_texts:
            return {
                "summary": "No recent memories found.",
                "trace": "",
                "source_count": 0,
            }

        # 🪞 Reflect on memory text
        prompt = self.build_summary_prompt(memory_texts)
        summary = self.generate_thought(prompt)

        self.log_thought(summary)
        set_cached_reflection(self.assistant.slug, summary)

        return {
            "summary": summary,
            "trace": prompt,
            "source_count": len(memory_texts),
        }

    def think(self) -> dict:
        prompt = "You are reasoning about the current project. What's your thought?"
        steps = [
            "Detected user is asking for clarification or summary.",
            f"Identified project name: '{self.project.title}'.",
            "Concluded that more context is needed to respond meaningfully.",
        ]

        try:
            thought = self.generate_thought(prompt)
            result = self.log_thought(
                content=thought,
                role="assistant",
                thought_type="cot",  # chain of thought
                steps=steps,
                model="gpt-4o",
            )

            return result  # already includes text, steps, model, created_at
        except Exception as e:
            logger.error(f"[think()] failed to generate thought: {e}", exc_info=True)
            return {
                "text": "⚠️ Thought generation failed.",
                "steps": [],
                "model": None,
                "created_at": None,
            }

    def delegate_objective(
        self,
        objective: "AssistantObjective",
        *,
        summary: str | None = None,
    ) -> Assistant:
        """Spawn a delegate agent to handle a specific objective."""

        project = objective.project
        thread = project.thread or project.narrative_thread

        child = spawn_delegated_assistant(
            self.assistant,
            project=project,
            name=f"{objective.title} Agent",
            description=objective.description or "",
            narrative_thread=thread,
            reason=f"objective:{objective.title}",
            summary=summary or objective.description or objective.title,
            objective=objective,
        )

        objective.delegated_assistant = child
        objective.save()

        log_assistant_thought(
            self.assistant,
            f"Delegated objective '{objective.title}' to {child.name}",
            thought_type="delegation",
            project=project,
        )

        return child
