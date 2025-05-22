"""Agent, Memory, and Document service classes."""
from typing import List, Optional
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from agents.models import Agent, AgentLegacy, AgentSkill, AgentSkillLink, SwarmMemoryEntry
from intel_core.models import Document
from memory.models import MemoryEntry


class MemoryService:
    """Helper service for memory related operations."""

    def record_agent_spawn(self, agent: Agent, skill: str) -> MemoryEntry:
        """Create a memory entry when a new agent is spawned."""
        return MemoryEntry.objects.create(
            event=f"Agent {agent.name} spawned with focus on {skill}",
            assistant=agent.parent_assistant,
            source_role="system",
            linked_content_type=ContentType.objects.get_for_model(Agent),
            linked_object_id=agent.id,
        )

    def record_swarm_event(self, title: str, content: str, agent: Agent) -> SwarmMemoryEntry:
        """Create a swarm memory entry linked to the agent."""
        entry = SwarmMemoryEntry.objects.create(
            title=title,
            content=content,
            origin="spawn",
        )
        entry.linked_agents.add(agent)
        return entry


class DocumentService:
    """Helper service for document queries."""

    def get_documents_for_skill(self, skill: str, limit: int = 3) -> List[Document]:
        """Return documents tagged with the given skill."""
        return list(Document.objects.filter(tags__name__iexact=skill)[:limit])

    def get_documents_by_ids(self, ids: List[str]) -> List[Document]:
        """Fetch documents by primary keys."""
        return list(Document.objects.filter(id__in=ids))


class AgentService:
    """Service encapsulating common agent workflows."""

    def __init__(self,
                 memory_service: Optional[MemoryService] = None,
                 document_service: Optional[DocumentService] = None):
        self.memory_service = memory_service or MemoryService()
        self.document_service = document_service or DocumentService()

    # ---------- Training ----------
    def train_agent_from_documents(self, agent: Agent, documents: List[Document]) -> dict:
        """Generate summary skills from docs and update the agent profile."""
        combined_text = "\n".join((doc.summary or doc.content[:200]) for doc in documents)
        prompt = (
            "Summarize key skills an AI agent would learn from these documents as a comma separated list."
        )
        prompt += "\n" + combined_text

        try:
            from utils.llm_router import call_llm

            parsed = call_llm(
                [{"role": "user", "content": prompt}],
                model="gpt-4o",
                temperature=0.2,
                max_tokens=150,
            )
            new_skills = [s.strip() for s in parsed.split(',') if s.strip()]
        except Exception:
            new_skills = []

        existing = {
            s.get("skill") if isinstance(s, dict) else str(s): s
            for s in (agent.verified_skills or [])
        }
        for name in new_skills:
            existing[name] = {
                "skill": name,
                "source": "training",
                "confidence": 0.6,
                "last_verified": timezone.now().isoformat(),
            }
        agent.verified_skills = list(existing.values())
        agent.skills = list({*agent.skills, *existing.keys()})
        for doc in documents:
            agent.trained_documents.add(doc)
        agent.save()

        return {"skills": agent.verified_skills, "trained": [str(d.id) for d in documents]}

    # ---------- Spawning ----------
    def spawn_agent_for_skill(self, skill: str, base_profile: dict) -> Agent:
        """Create a specialized agent for the given skill gap."""
        name = base_profile.get("name") or f"{skill.title()} Specialist"
        agent = Agent.objects.create(
            name=name,
            description=base_profile.get("description", ""),
            specialty=skill,
            metadata=base_profile.get("metadata", {}),
            preferred_llm=base_profile.get("preferred_llm", "gpt-4o"),
            execution_mode=base_profile.get("execution_mode", "direct"),
            parent_assistant=base_profile.get("parent_assistant"),
        )

        skill_obj, _ = AgentSkill.objects.get_or_create(name=skill)
        AgentSkillLink.objects.create(agent=agent, skill=skill_obj, source="spawn")

        docs = self.document_service.get_documents_for_skill(skill)
        if docs:
            self.train_agent_from_documents(agent, docs)

        # memory logging
        self.memory_service.record_agent_spawn(agent, skill)
        self.memory_service.record_swarm_event(
            title=f"Agent spawned: {agent.name}",
            content=f"Agent {agent.name} created for skill {skill}",
            agent=agent,
        )

        AgentLegacy.objects.get_or_create(agent=agent)
        return agent

