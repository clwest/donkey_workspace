import logging
from django.utils.text import slugify
from typing import List

from assistants.models.assistant import Assistant, DelegationEvent
from memory.models import MemoryEntry
from mcp_core.models import MemoryContext, Tag
from utils.llm_router import call_llm

logger = logging.getLogger(__name__)


class DelegationSummaryEngine:
    """Generate a concise summary of delegation memories for an assistant."""

    def __init__(self, assistant: Assistant):
        self.assistant = assistant
        if not assistant.memory_context:
            ctx, _ = MemoryContext.objects.get_or_create(
                content=f"{assistant.slug} context"
            )
            assistant.memory_context = ctx
            assistant.save(update_fields=["memory_context"])
        self.context = assistant.memory_context

    def _format_history(self, entries: List[MemoryEntry]) -> str:
        lines = []
        for mem in entries:
            agents = [a.name for a in mem.linked_agents.all()]
            if not agents and mem.linked_object_id and mem.linked_content_type:
                if mem.linked_content_type.model == "delegationevent":
                    try:
                        event = DelegationEvent.objects.get(id=mem.linked_object_id)
                        agents.append(event.child_assistant.name)
                    except DelegationEvent.DoesNotExist:
                        pass
            preview = mem.summary or mem.full_transcript or mem.event
            preview = preview.splitlines()[0][:120]
            if agents:
                lines.append(f"{preview} -> {', '.join(agents)}")
            else:
                lines.append(preview)
        return "\n".join(lines)

    def _compress_history(self, text: str) -> str:
        """Optionally compress very long history logs using the LLM."""
        if len(text) <= 4000:
            return text
        prompt = (
            "Summarize the following delegation history in under 300 words:\n\n"
            f"{text}"
        )
        try:  # pragma: no cover - external call
            return call_llm(
                [{"role": "user", "content": prompt}],
                model=getattr(self.assistant, "preferred_model", "gpt-4o"),
                max_tokens=400,
            )
        except Exception as exc:  # pragma: no cover - external call
            logger.error("Delegation compression failed: %s", exc)
            return text[:4000]

    def save_to_memory(self, summary_text: str, full_text: str, qs) -> MemoryEntry:
        """Persist the delegation summary to memory with tagging."""
        entry = MemoryEntry.objects.create(
            assistant=self.assistant,
            context=self.context,
            type="delegation_summary",
            event="Delegation summary",
            summary=summary_text,
            full_transcript=full_text,
            importance=6,
            source_role="assistant",
        )
        tags = ["delegation", "delegation_summary"]
        agent_slugs = set()
        for mem in qs:
            agent_slugs.update(a.slug for a in mem.linked_agents.all())
        for slug in agent_slugs:
            tags.append(f"agent:{slug}")
        tag_objs = []
        for name in tags:
            tag, _ = Tag.objects.get_or_create(
                slug=slugify(name), defaults={"name": name}
            )
            tag_objs.append(tag)
        if tag_objs:
            entry.tags.add(*tag_objs)
        return entry

    def summarize_delegations(self) -> MemoryEntry:
        qs = MemoryEntry.objects.filter(
            assistant=self.assistant,
            type="delegation",
            context=self.context,
        ).prefetch_related("linked_agents")
        count = qs.count()
        if count == 0:
            summary_text = "No delegation history found."
            history_text = ""
        else:
            formatted = self._format_history(list(qs.order_by("created_at")))
            history_text = self._compress_history(formatted)
            prompt = (
                f"You are summarizing all recent task delegations performed by the assistant {self.assistant.name}.\n\n"
                "Below are recorded memory logs of delegation events.\n\n"
                "Identify:\n"
                "- Who tasks were delegated to (agent names)\n"
                "- The types of tasks or objectives\n"
                "- Whether the outcome was successful or required follow-up\n"
                "- Any recurring issues or patterns in delegation behavior\n\n"
                "Use 4–8 bullet points to summarize key insights, followed by a paragraph reflection if needed.\n\n"
                f"Memories:\n{formatted}"
            )
            try:
                summary_text = call_llm(
                    [{"role": "user", "content": prompt}],
                    model=getattr(self.assistant, "preferred_model", "gpt-4o"),
                    max_tokens=400,
                )
            except Exception as exc:  # pragma: no cover - external call
                logger.error("Delegation summary failed: %s", exc)
                summary_text = "Delegation summary failed."
        return self.save_to_memory(summary_text, history_text, qs)
