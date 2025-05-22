from typing import Optional, List, Any
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from utils.llm_router import call_llm

FAREWELL_TEMPLATE = (
    "Agent {agent_name} has completed their mission as part of the {cluster_name} cluster.\n\n"
    "Skills contributed: {skills}\n"
    "Last active: {last_active}\n\n"
    "Legacy Note:\n{legacy_notes}\n\n"
    "Farewell, and thank you for your service."
)


from mcp_core.models import MemoryContext, Plan, Task, ActionLog, Tag
from agents.models import (
    Agent,
    AgentThought,
    AgentTrainingAssignment,
    AgentSkill,
    AgentSkillLink,
    AgentLegacy,
    FarewellTemplate,
    SwarmMemoryEntry,
    AgentCluster,
)

from embeddings.helpers.helpers_io import save_embedding

User = settings.AUTH_USER_MODEL


def _skill_names(skills: list) -> List[str]:
    names = []
    for s in skills or []:
        if isinstance(s, dict) and s.get("skill"):
            names.append(s["skill"])
        elif isinstance(s, str):
            names.append(s)
    return names


def render_farewell(agent: Agent, reason: str = "") -> str:
    cluster = agent.clusters.first()
    cluster_name = cluster.name if cluster else "swarm"
    skills = ", ".join(_skill_names(agent.verified_skills)) or "None"
    legacy = getattr(agent, "agentlegacy", None)
    legacy_notes = legacy.legacy_notes if legacy else ""
    last_active = agent.updated_at.strftime("%Y-%m-%d") if agent.updated_at else "n/a"
    return FAREWELL_TEMPLATE.format(
        agent_name=agent.name,
        cluster_name=cluster_name,
        skills=skills,
        last_active=last_active,
        legacy_notes=legacy_notes,
    )


class AgentController:
    def __init__(self, user: Optional[Any] = None):
        self.user = user

    def reflect(
        self,
        content: str,
        important: bool = False,
        category: Optional[str] = None,
        tag_names: Optional[List[str]] = None,
    ) -> MemoryContext:
        memory = MemoryContext.objects.create(
            target_content_type=ContentType.objects.get_for_model(get_user_model()),
            target_object_id=self.user.id if self.user else None,
            content=content,
            important=important,
            category=category,
        )

        if tag_names:
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(
                    name=name, defaults={"slug": name.lower().replace(" ", "-")}
                )
                memory.tags.add(tag)

        self.log_action("reflect", f"Saved reflection: {content[:60]}")
        save_embedding(memory)
        return memory

    def create_plan(
        self,
        title: str,
        description: str = "",
        memory_context: Optional[MemoryContext] = None,
    ) -> Plan:
        plan = Plan.objects.create(
            title=title,
            description=description,
            memory_context=memory_context,
            created_by=self.user,
        )
        self.log_action("create", f"Created plan: {title}")
        save_embedding(plan)
        return plan

    def create_task(
        self,
        title: str,
        plan: Optional[Plan] = None,
        description: str = "",
        project: Optional[str] = None,
        assigned_to: Optional[Agent] = None,
    ) -> Task:
        task = Task.objects.create(
            title=title,
            description=description,
            plan=plan,
            project=project,
            assigned_to=assigned_to,
        )
        self.log_action("create", f"Created task: {title}")
        save_embedding(task)
        return task

    def assign_agent(self, task: Task, agent: Agent) -> Task:
        task.assigned_to = agent
        task.save()
        self.log_action(
            "assign", f"Assigned task '{task.title}' to agent '{agent.name}'"
        )
        return task

    def log_action(
        self,
        action_type: str,
        description: str,
        related_agent: Optional[Agent] = None,
        related_task: Optional[Task] = None,
        related_plan: Optional[Plan] = None,
    ) -> ActionLog:
        return ActionLog.objects.create(
            action_type=action_type,
            description=description,
            performed_by=self.user,
            related_agent=related_agent,
            related_task=related_task,
            related_plan=related_plan,
        )

    def think_with_agent(self, agent: Agent) -> str:
        prompt = f"""
        You are an AI agent named {agent.name}.
        Your specialty is: {agent.specialty or 'general problem solving'}.
        Purpose: {agent.metadata.get('purpose', '...') if agent.metadata else '...'}

        What are your current internal thoughts based on your identity and purpose?
        """

        thought_trace = ["Generated agent identity and purpose prompt."]

        thought = call_llm(
            [{"role": "user", "content": prompt}],
            model="gpt-4o",
            temperature=0.7,
            max_tokens=300,
        )
        thought = thought.strip()
        thought_trace.append("Received model response.")

        log = AgentThought.objects.create(
            agent=agent,
            thought=thought,
            thought_trace="\n".join(f"• {s}" for s in thought_trace),
        )

        save_embedding(log)
        return thought

    def chat_with_agent(
        self, agent: Agent, message: str, context: Optional[str] = None
    ) -> str:
        system_prompt = f"You are an AI agent named {agent.name}."
        if agent.specialty:
            system_prompt += f" Specialty: {agent.specialty}."
        if agent.metadata and agent.metadata.get("description"):
            system_prompt += f" Description: {agent.metadata['description']}"

        full_context = f"{context or ''}\n\nUser: {message}".strip()

        reply = call_llm(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_context},
            ],
            model="gpt-4o",
            temperature=0.7,
            max_tokens=500,
        ).strip()

        memory = MemoryContext.objects.create(
            target_content_type=ContentType.objects.get_for_model(Agent),
            target_object_id=agent.id,
            content=f"User: {message}\nAgent: {reply}",
            important=False,
            category="agent_chat",
        )
        save_embedding(memory)

        self.log_action("chat", f"Chatted with {agent.name}", related_agent=agent)

        return reply

    def log_thought(
        self, agent: Agent, thought: str, trace: Optional[List[str]] = None
    ) -> AgentThought:
        log = AgentThought.objects.create(
            agent=agent,
            thought=thought,
            thought_trace="\n".join(f"• {s}" for s in (trace or [])),
        )
        save_embedding(log)
        return log


# codex-optimize:feedback-profile
def update_agent_profile_from_feedback(
    agent: Agent, feedback_logs: List["AgentFeedbackLog"]
):
    """Update agent metadata fields based on feedback logs."""
    if agent.metadata is None:
        agent.metadata = {}
    tags = set(agent.metadata.get("tags", [])) | set(agent.tags or [])
    skills = set(agent.metadata.get("skills", [])) | set(
        _skill_names(agent.verified_skills)
    )
    scores = []

    for log in feedback_logs:
        words = [w.strip(".,! ").lower() for w in log.feedback_text.split()]
        tags.update({w for w in words if len(w) > 4})
        if log.score is not None:
            scores.append(log.score)

    if scores:
        agent.strength_score = sum(scores) / len(scores)

    agent.metadata["tags"] = list(tags)
    agent.metadata["skills"] = list(skills)
    agent.metadata["last_updated"] = timezone.now().isoformat()
    agent.tags = list(tags)
    agent.skills = list(skills)
    agent.verified_skills = [
        {
            "skill": s,
            "source": "feedback",
            "confidence": 0.5,
            "last_verified": timezone.now().isoformat(),
        }
        for s in skills
    ]
    agent.save()

    return {
        "tags": list(tags),
        "skills": list(skills),
        "strength_score": agent.strength_score,
    }

    # CODEx MARKER: recommend_agent_for_task
    def recommend_agent_for_task(
        self, task_description: str, thread
    ) -> Optional[Agent]:
        """Select an agent based on tags, specialty, and thread overlap."""
        from agents.models import Agent as AgentModel
        from memory.models import MemoryEntry

        candidates = AgentModel.objects.all()
        best_score = 0.0
        best_agent = None
        task_lower = task_description.lower()
        thread_tags = (
            set(t.name.lower() for t in thread.tags.all())
            if hasattr(thread, "tags")
            else set()
        )

        for agent in candidates:
            readiness = getattr(agent, "readiness_score", 0.0)
            if readiness < 0.75:
                continue

            score = 0.0

            for skill in _skill_names(agent.verified_skills):
                if skill.lower() in task_lower:
                    score += 0.6
                    break

            if (
                AgentTrainingAssignment.objects.filter(agent=agent, completed=True)
                .order_by("-completed_at")
                .exists()
            ):
                score += 0.3

            if agent.specialty:
                for tag in thread_tags:
                    if tag in agent.specialty.lower():
                        score += 0.2
                        break

            if task_lower in (agent.description or "").lower():
                score += 0.1

            if MemoryEntry.objects.filter(
                narrative_thread=thread, assistant=agent.parent_assistant
            ).exists():
                score += 0.2

            if score > best_score:
                best_score = score
                best_agent = agent

        if best_agent:
            return best_agent

        # Fallback to basic tag/specialty matching
        best_score = 0.0
        for agent in candidates:
            score = 0.0
            if agent.specialty:
                for tag in thread_tags:
                    if tag in agent.specialty.lower():
                        score += 0.5
                        break
            if task_lower in (agent.description or "").lower():
                score += 0.2
            if MemoryEntry.objects.filter(
                narrative_thread=thread, assistant=agent.parent_assistant
            ).exists():
                score += 0.3
            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent


# codex-optimize:training
def train_agent_from_documents(agent: Agent, documents: List["Document"]) -> dict:
    """Generates summary skills from docs, embeds them, and updates agent profile."""
    from intel_core.models import Document

    combined_text = "\n".join((doc.summary or doc.content[:200]) for doc in documents)
    prompt = "Summarize key skills an AI agent would learn from these documents as a comma separated list."
    prompt += "\n" + combined_text

    try:
        parsed = call_llm(
            [{"role": "user", "content": prompt}],
            model="gpt-4o",
            temperature=0.2,
            max_tokens=150,
        )
        new_skills = [s.strip() for s in parsed.split(",") if s.strip()]
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


def recommend_training_documents(agent: Agent) -> List["Document"]:
    """Return top recent documents that may fill gaps in the agent profile."""
    from intel_core.models import Document

    recent_docs = Document.objects.order_by("-created_at")[:50]
    agent_tags = set(agent.tags or [])
    scored = []
    for doc in recent_docs:
        doc_tags = set(doc.tags.values_list("name", flat=True))
        score = len(agent_tags & doc_tags)
        title_summary = (doc.title + " " + (doc.summary or "")).lower()
        for skill in _skill_names(agent.verified_skills):
            if skill.lower() in title_summary:
                score += 1
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:5]]


def evaluate_agent_lifecycle(agent: Agent) -> dict:
    """Return lifecycle action suggestion for the agent."""
    from mcp_core.models import ActionLog
    from agents.models import AgentCluster, AgentFeedbackLog
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    last_action = (
        ActionLog.objects.filter(related_agent=agent).order_by("-created_at").first()
    )
    days_since_action = (now - last_action.created_at).days if last_action else 999
    recent_feedback = AgentFeedbackLog.objects.filter(
        agent=agent, created_at__gte=now - timedelta(days=7)
    ).exists()
    active_cluster = AgentCluster.objects.filter(agents=agent, is_active=True).exists()

    if not active_cluster or days_since_action > 30:
        return {"action": "archive", "reason": "inactive or cluster dissolved"}
    if agent.readiness_score < 0.5 or not recent_feedback:
        return {"action": "retrain", "reason": "low readiness or stale feedback"}
    return {"action": "keep", "reason": "agent active"}


def find_complementary_agents(
    target_agent: Agent, required_skills: List[str]
) -> List[Agent]:
    """Return agents with matching or related skills based on the skill graph."""
    skill_names = {s.lower() for s in required_skills}
    related = set()
    for name in list(skill_names):
        try:
            skill_obj = AgentSkill.objects.get(name__iexact=name)
            related.update(skill_obj.related_skills.values_list("name", flat=True))
        except AgentSkill.DoesNotExist:
            continue
    search_names = skill_names | {s.lower() for s in related}
    skills = AgentSkill.objects.filter(name__in=search_names)
    agent_ids = (
        AgentSkillLink.objects.filter(skill__in=skills)
        .exclude(agent=target_agent)
        .values_list("agent_id", flat=True)
    )
    return list(Agent.objects.filter(id__in=agent_ids).distinct())


def recommend_agent_resurrection(skill: str) -> Optional[Agent]:
    """
    Finds an archived agent with matching or related skills.
    If task demands it, suggest reactivation.
    """
    from datetime import timedelta

    thirty_days_ago = timezone.now() - timedelta(days=30)

    try:
        base_skill = AgentSkill.objects.get(name__iexact=skill)
        related = list(base_skill.related_skills.all())
        skills = [base_skill] + related
    except AgentSkill.DoesNotExist:
        skills = []

    links = AgentSkillLink.objects.filter(skill__in=skills, strength__gte=0.6)
    agent_ids = links.values_list("agent_id", flat=True)
    candidates = (
        Agent.objects.filter(id__in=agent_ids, is_active=False)
        .filter(
            models.Q(reactivated_at__isnull=True)
            | models.Q(reactivated_at__lt=thirty_days_ago)
        )
        .order_by("-strength_score")
    )
    return candidates.first()


def resurrect_agent(agent: Agent, by_assistant: Optional["Assistant"] = None) -> Agent:
    """Reactivate an archived agent and update its legacy."""
    agent.is_active = True
    agent.reactivated_at = timezone.now()
    agent.save(update_fields=["is_active", "reactivated_at"])

    legacy, _ = AgentLegacy.objects.get_or_create(agent=agent)
    legacy.resurrection_count += 1
    legacy.save(update_fields=["resurrection_count", "updated_at"])

    entry = SwarmMemoryEntry.objects.create(
        title=f"Agent resurrected: {agent.name}",
        content=f"{agent.name} was reactivated",
        origin="resurrection",
    )
    entry.linked_agents.add(agent)
    if by_assistant and getattr(by_assistant, "current_project", None):
        entry.linked_projects.add(by_assistant.current_project)
    return agent


def resurrect_legacy_agent(legacy: AgentLegacy, reason: str) -> Agent:
    """Spawn a new agent from legacy data and log the resurrection."""
    source = legacy.agent
    new_agent = Agent.objects.create(
        name=source.name,
        description=source.description,
        specialty=source.specialty,
        metadata=source.metadata,
        preferred_llm=source.preferred_llm,
        execution_mode=source.execution_mode,
        agent_type=source.agent_type,
        parent_assistant=source.parent_assistant,
    )

    new_agent.tags = list(source.tags)
    new_agent.skills = list(source.skills)
    new_agent.save()

    for link in AgentSkillLink.objects.filter(agent=source):
        AgentSkillLink.objects.create(
            agent=new_agent, skill=link.skill, source="legacy-resurrection"
        )

    for cluster in source.clusters.all():
        cluster.agents.add(new_agent)

    legacy.resurrection_count += 1
    legacy.save(update_fields=["resurrection_count", "updated_at"])

    entry = SwarmMemoryEntry.objects.create(
        title=f"Legacy Agent Resurrected: {source.name}",
        content=reason,
        origin="resurrection",
    )
    entry.linked_agents.add(new_agent)
    entry.linked_agents.add(source)

    from mcp_core.models import Tag

    for name in ["resurrected", "seasonal", "legacy-return"]:
        tag, _ = Tag.objects.get_or_create(name=name, defaults={"slug": name})
        entry.tags.add(tag)

    return new_agent


def record_project_completion(project: "AssistantProject") -> None:
    """Increment mission counters for all agents in the project."""
    for agent in project.agents.all():
        legacy, _ = AgentLegacy.objects.get_or_create(agent=agent)
        legacy.missions_completed += 1
        legacy.save(update_fields=["missions_completed", "updated_at"])


def retire_agent(
    agent: Agent, reason: str, farewell_text: Optional[str] = None
) -> SwarmMemoryEntry:
    """Archive the agent and record a farewell message."""
    agent.is_active = False
    agent.save(update_fields=["is_active"])

    legacy, _ = AgentLegacy.objects.get_or_create(agent=agent)

    if not farewell_text:
        template = FarewellTemplate.objects.order_by("-created_at").first()
        if template:
            farewell_text = template.content
        else:
            farewell_text = (
                "Agent {{ agent.name }} has completed their mission as part of the {{ cluster.name }} cluster.\n\n"
                "Skills contributed: {{ skills }}\n"
                "Last active: {{ last_active }}\n\n"
                'Legacy Note:\n"{{ legacy_notes }}"\n\n'
                "Farewell, and thank you for your service."
            )

    cluster = agent.clusters.first()
    context = {
        "agent": agent,
        "cluster": cluster or {},
        "skills": ", ".join(agent.skills or []),
        "last_active": agent.updated_at.strftime("%Y-%m-%d"),
        "legacy_notes": legacy.legacy_notes or "",
    }

    farewell = farewell_text
    for key, val in context.items():
        placeholder = "{{ " + key + " }}"
        farewell = farewell.replace(placeholder, str(val))

    entry = SwarmMemoryEntry.objects.create(
        title=f"Agent retired: {agent.name}",
        content=farewell,
        origin="retirement",
    )
    entry.linked_agents.add(agent)
    from mcp_core.models import Tag

    for name in ["farewell", "retired", "mentor-passed"]:
        tag, _ = Tag.objects.get_or_create(name=name, defaults={"slug": name})
    entry.tags.add(tag)

    return entry


def realign_agent(agent: Agent, target_cluster: AgentCluster) -> str:
    """Move an agent to a new cluster and log the realignment."""
    # Remove from existing clusters
    for cluster in agent.clusters.all():
        cluster.agents.remove(agent)
    target_cluster.agents.add(agent)
    agent.tags = list(set(agent.tags or []) - {str(c.id) for c in agent.clusters.all()})
    agent.save(update_fields=["tags", "updated_at"])

    entry = SwarmMemoryEntry.objects.create(
        title=f"Agent Realigned: {agent.name}",
        content=f"Moved to cluster {target_cluster.name}",
        origin="realignment",
    )
    entry.linked_agents.add(agent)
    entry.linked_projects.set(
        [target_cluster.project] if target_cluster.project else []
    )
    from mcp_core.models import Tag
    from django.utils.text import slugify

    tags = []
    for name in ["realignment", "mission_shift"]:
        tag, _ = Tag.objects.get_or_create(name=name, defaults={"slug": slugify(name)})
        tags.append(tag)
    entry.tags.set(tags)

    return f"Agent {agent.name} realigned to {target_cluster.name}"
