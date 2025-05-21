import logging
from assistants.models import (
    AssistantReflectionLog,
    Assistant,
    AssistantProject,
    AssistantReflectionInsight,
    AssistantThoughtLog,
)
from mcp_core.models import MemoryContext, DevDoc, NarrativeThread
from intel_core.models import Document
from memory.models import MemoryEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from assistants.models import AssistantProject
from utils.llm_router import call_llm
from agents.models import (
    Agent,
    AgentTrainingAssignment,
    AgentFeedbackLog,
    AgentSkill,
    AgentSkillLink,
)

logger = logging.getLogger(__name__)


def _skill_names(skills: list) -> list[str]:
    names = []
    for s in skills or []:
        if isinstance(s, dict) and s.get("skill"):
            names.append(s["skill"])
        elif isinstance(s, str):
            names.append(s)
    return names


def reflect_on_agent_training(assistant: Assistant, agent: Agent) -> str:
    """
    Generates a reflection summary for an agent's recent training progress.
    Returns a markdown string with bullet points.
    """

    assignments = AgentTrainingAssignment.objects.filter(agent=agent)
    total = assignments.count()
    completed = assignments.filter(completed=True).count()
    completion_rate = completed / total if total else 0.0

    skill_tags = set()
    for a in assignments:
        skill_tags.update(a.document.tags.values_list("name", flat=True))

    feedback_logs = list(
        AgentFeedbackLog.objects.filter(agent=agent, score__isnull=False).order_by(
            "-created_at"
        )[:6]
    )
    recent_scores = [f.score for f in feedback_logs[:3]]
    past_scores = [f.score for f in feedback_logs[3:]]
    recent_avg = sum(recent_scores) / len(recent_scores) if recent_scores else 0.0
    past_avg = sum(past_scores) / len(past_scores) if past_scores else 0.0
    if recent_avg > past_avg + 0.05:
        trajectory = "improving"
    elif recent_avg + 0.05 < past_avg:
        trajectory = "declining"
    else:
        trajectory = "stable"

    readiness = max(agent.readiness_score, completion_rate)

    lines = [
        f"- Training completion rate: {completion_rate:.0%} ({completed}/{total})",
    ]
    if skill_tags:
        lines.append("- Acquired skills: " + ", ".join(sorted(skill_tags)))
    if agent.verified_skills:
        lines.append(
            "- Verified skills: " + ", ".join(_skill_names(agent.verified_skills))
        )
    lines.append(f"- Task performance trajectory appears **{trajectory}**")
    lines.append(f"- Suggested readiness score: {readiness:.2f}")
    lines.append("- Next steps: continue practicing and gather more feedback")

    return "\n".join(lines)


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

    Was your tone appropriate for the tasks assigned?
    Would a different emotional state have produced better results?
    """

    def generate_reflection(self, prompt: str, temperature: float = 0.5) -> str:
        return call_llm(
            [{"role": "user", "content": prompt}],
            model=self.assistant.preferred_model or "gpt-4o",
            temperature=temperature,
            max_tokens=400,
        )

    def reflect_now(
        self,
        context: MemoryContext,
        *,
        scene: str | None = None,
        location_context: str | None = None,
    ) -> AssistantReflectionLog:
        """Run a quick reflection over recent memories for the given context."""

        from assistants.helpers.memory_helpers import get_relevant_memories_for_task

        entries = get_relevant_memories_for_task(
            self.assistant,
            project=self.project,
            task_type="reflection",
            context=context,
            limit=30,
        )
        texts = [e.event.strip() for e in entries if e.event.strip()]
        if scene or location_context:
            loc_parts = []
            if scene:
                loc_parts.append(f"Scene: {scene}")
            if location_context:
                loc_parts.append(location_context)
            texts.insert(0, " | ".join(loc_parts))

        prompt = None
        if texts:
            prompt = self.build_reflection_prompt(texts)

        try:
            reflection_text = (
                self.generate_reflection(prompt) if prompt else "No meaningful content."
            )

            log = AssistantReflectionLog.objects.create(
                assistant=self.assistant,
                project=self.project,
                title=f"Reflection for context {context.id}",
                summary=reflection_text,
                raw_prompt=prompt,
            )

            MemoryEntry.objects.create(
                event=reflection_text,
                assistant=self.assistant,
                source_role="assistant",
                linked_content_type=ContentType.objects.get_for_model(self.assistant),
                linked_object_id=self.assistant.id,
                is_conversation=False,
                context=context,
            )

            if scene:
                AssistantThoughtLog.objects.create(
                    assistant=self.assistant,
                    thought=f"Location {scene} considered during reflection",
                    thought_type="scene_match",
                    origin="automatic",
                )

            logger.info(f"[🧠] Reflection saved for context {context.id}.")
            return log
        except Exception as e:
            logger.error(f"[❌] Reflection failed: {e}", exc_info=True)
            raise

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
                "preferred_model": "ollama:mistral",
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

    def reflect_on_memory(self, memory: MemoryEntry) -> AssistantReflectionLog | None:
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
            reflection_text = self.generate_reflection(prompt)

            log = AssistantReflectionLog.objects.create(
                project=self.project,
                assistant=self.assistant,
                linked_memory=memory,
                title=f"Reflection on memory {memory.id}",
                summary=reflection_text,
                raw_prompt=prompt,
                category="meta",
            )

            logger.info(f"[✅] Reflection log created for memory {memory.id}")
            return log
        except Exception as e:
            logger.error(
                f"[❌] Failed to reflect on memory {memory.id}: {e}", exc_info=True
            )
            return None

    def reflect_on_assistant(
        self, assistant: Assistant, project: AssistantProject
    ) -> AssistantReflectionLog:
        """Generate a reflection about a newly spawned assistant."""
        prompt = f"""You are {self.assistant.name}, reflecting on a delegated assistant you created.\n\n" \
                f"Assistant Name: {assistant.name}\n" \
                f"Specialty: {assistant.specialty or '(unspecified)'}\n" \
                f"Description: {assistant.description or '(none)'}\n" \
                "Provide constructive feedback on its purpose, tone, and any improvements."\
                "\nWas your tone appropriate for the tasks assigned?"\
                "\nWould a different emotional state have produced better results?"""
        reflection_text = self.generate_reflection(prompt)
        log = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            project=project,
            summary=reflection_text,
            raw_prompt=prompt,
            title=f"Reflection on assistant {assistant.name}",
        )
        return log

    # CODEx MARKER: plan_from_thread_context


def plan_from_thread_context(
    self,
    thread: "NarrativeThread",
    assistant: Assistant,
    project: AssistantProject | None = None,
):
    """Generate next actions from a narrative thread."""
    from agents.utils.agent_controller import AgentController
    from assistants.models import AssistantObjective, AssistantNextAction

    project = project or self.get_or_create_project(assistant)
    objective = (
        AssistantObjective.objects.filter(project=project, assistant=assistant)
        .order_by("created_at")
        .first()
    )
    if not objective:
        objective = AssistantObjective.objects.create(
            project=project,
            assistant=assistant,
            title=f"Thread: {thread.title}",
            description=thread.summary or "",
        )

    summary = thread.continuity_summary or thread.summary or thread.title
    prompt = (
        f"You are planning actions for the thread '{thread.title}'. "
        f"Context: {summary}\n"
        "List 3 to 5 short actionable next steps."
    )
    try:
        output = call_llm(
            [{"role": "user", "content": prompt}],
            model=assistant.preferred_model or "gpt-4o",
            temperature=0.4,
            max_tokens=300,
        )
    except Exception as e:
        logger.error(f"plan_from_thread_context failed: {e}")
        output = "- Review recent memories\n- Clarify goals"

    lines = [l.strip("- •\t ") for l in output.splitlines() if l.strip()]
    lines = [l for l in lines if l][:5]
    controller = AgentController()
    actions = []
    for idx, line in enumerate(lines):
        agent = controller.recommend_agent_for_task(line, thread)
        action = AssistantNextAction.objects.create(
            objective=objective,
            content=line,
            assigned_agent=agent,
            linked_thread=thread,
            importance_score=max(0.0, 1.0 - idx * 0.1),
        )
        actions.append(action)
    return actions


def evaluate_thought_continuity(
    self, *, project: AssistantProject | None = None
) -> dict:
    """Assess continuity of recent thoughts and suggest next actions."""

    qs = AssistantThoughtLog.objects.filter(assistant=self.assistant)
    if project:
        qs = qs.filter(project=project)

    recent = list(qs.order_by("-created_at")[:5])
    if not recent:
        return {
            "continuity_score": 1.0,
            "recent_thoughts": [],
            "suggestions": [],
        }

    expected_thread = None
    if project:
        expected_thread = project.thread or project.narrative_thread
    if not expected_thread:
        expected_thread = recent[0].narrative_thread

    total = len(recent)
    aligned = sum(
        1
        for t in recent
        if t.narrative_thread_id == getattr(expected_thread, "id", None)
    )
    score = aligned / total if total else 1.0

    suggestions = []
    if score < 0.6:
        suggestions.append("review recent events and reconnect to the main thread")

    return {
        "continuity_score": round(score, 2),
        "recent_thoughts": [
            {
                "id": str(t.id),
                "text": t.thought,
                "thread": str(t.narrative_thread_id) if t.narrative_thread_id else None,
            }
            for t in recent
        ],
        "thread_id": str(expected_thread.id) if expected_thread else None,
        "suggestions": suggestions,
    }


# codex-coach:assign-training
def assign_training_documents(
    assistant: Assistant, agent: "Agent", docs: list["Document"], train: bool = True
) -> list["AgentTrainingAssignment"]:
    """Assign documents to an agent and optionally trigger training."""
    from agents.models import AgentTrainingAssignment
    from agents.utils.agent_controller import train_agent_from_documents

    assignments = []
    for doc in docs:
        assignment = AgentTrainingAssignment.objects.create(
            assistant=assistant,
            agent=agent,
            document=doc,
        )
        assignments.append(assignment)

    if train and docs:
        result = train_agent_from_documents(agent, list(docs))
        AgentTrainingAssignment.objects.filter(
            id__in=[a.id for a in assignments]
        ).update(status="complete")
        logger.info(
            f"[Training] Agent {agent.name} trained on {len(docs)} documents: {result}"
        )

    return assignments


# codex-coach:evaluate-training
def evaluate_agent_training(assistant: Assistant, agent: "Agent") -> dict:
    """Summarize training progress and return readiness report."""
    from agents.models import AgentTrainingAssignment, AgentFeedbackLog

    assignments = AgentTrainingAssignment.objects.filter(
        agent=agent, assistant=assistant
    )
    completed = assignments.filter(status="complete").count()
    pending = assignments.filter(status="pending").count()
    feedback_scores = list(
        AgentFeedbackLog.objects.filter(agent=agent, score__isnull=False).values_list(
            "score", flat=True
        )
    )
    avg_score = sum(feedback_scores) / len(feedback_scores) if feedback_scores else None

    tags = set(agent.tags or [])
    skills = set(_skill_names(agent.verified_skills))

    report = {
        "completed_assignments": completed,
        "pending_assignments": pending,
        "avg_feedback": avg_score,
        "skills": list(skills),
        "tags": list(tags),
    }

    if avg_score is not None and avg_score < 0.5:
        report["next_steps"] = "Increase targeted practice on low-scoring areas"
    elif pending:
        report["next_steps"] = "Complete pending training assignments"
    else:
        report["next_steps"] = "Agent ready for advanced tasks"

    return report


def reflect_on_agent_network(assistant: Assistant) -> str:
    """Generate a reflection on the assistant's agent network."""
    agents = list(assistant.assigned_agents.all())
    snapshot_lines = []
    for a in agents:
        assignments = AgentTrainingAssignment.objects.filter(agent=a).count()
        feedback = AgentFeedbackLog.objects.filter(
            agent=a, score__isnull=False
        ).order_by("-created_at")[:3]
        avg = sum(f.score for f in feedback) / len(feedback) if feedback else 0.0
        snapshot_lines.append(
            f"{a.name}: {assignments} trainings, avg feedback {avg:.2f}"
        )

    context = "\n".join(snapshot_lines)
    prompt = f"""### Assistant Agent Reflection

You are {assistant.name}, supervising a network of agents.

Based on the latest training assignments, feedback logs, and the shared skill graph, reflect on the following:

- Which agents have improved the most?
- Are there skill gaps or overlaps?
- Which agents are underutilized or overloaded?
- Suggest any skill clusters or role specializations.
- Recommend new training paths or delegation strategies.

Agents snapshot:\n{context}\n\nReturn a markdown summary in 4-6 bullet points."""

    try:
        return call_llm(
            [{"role": "user", "content": prompt}],
            model=assistant.preferred_model or "gpt-4o",
            temperature=0.4,
        )
    except Exception:
        return "- Unable to generate reflection."


def reflect_on_agent_swarm(assistant: Assistant) -> str:
    """
    Reflects on collaboration dynamics, training coverage, and mentoring bottlenecks.
    Summarizes recent agent interactions and proposes coordination improvements.
    """
    agents = list(assistant.assigned_agents.all())
    if not agents:
        return "- No agents assigned."

    mentoring_entries = (
        MemoryEntry.objects.filter(linked_agents__in=agents, tags__name__iexact="mentoring")
        .order_by("-created_at")[:20]
    )
    interaction_lines = []
    for m in mentoring_entries:
        interaction_lines.append(f"- {m.event}")

    agent_lines = []
    for a in agents:
        taught = sum(1 for m in mentoring_entries if m.event.startswith(a.name))
        learned = sum(1 for m in mentoring_entries if f"taught {a.name}" in m.event)
        agent_lines.append(f"{a.name}: taught {taught}, learned {learned}")

    context = "\n".join(agent_lines + interaction_lines)

    prompt = f"""### Agent Swarm Reflection

You are {assistant.name}, overseeing a swarm of agents.
Review the recent mentoring interactions and suggest ways to coordinate training better.

Points to consider:
- Which agents are mentoring vs being mentored?
- Are skills distributed evenly?
- Are there idle agents with teachable strengths?
- Propose mentoring pairs or tag gaps.

Data:\n{context}\n\nReturn a brief markdown summary."""

    try:
        return call_llm(
            [{"role": "user", "content": prompt}],
            model=assistant.preferred_model or "gpt-4o",
            temperature=0.4,
        )
    except Exception:
        return "- Unable to generate reflection."


def reflect_on_agent_clusters(assistant: Assistant) -> str:
    """Summarize agent clusters and suggest lifecycle actions."""
    from agents.models import AgentCluster
    from agents.utils.agent_controller import evaluate_agent_lifecycle
    clusters = AgentCluster.objects.filter(project__assistant=assistant)
    if not clusters.exists():
        return "- No clusters found."

    lines = []
    suggestions = []
    for c in clusters:
        names = ", ".join(c.agents.values_list("name", flat=True))
        lines.append(f"- **{c.name}**: {c.purpose} ({names})")
        for agent in c.agents.all():
            result = evaluate_agent_lifecycle(agent)
            if result["action"] != "keep":
                suggestions.append(f"{agent.name} → {result['action']} ({result['reason']})")

    if not suggestions:
        suggestions.append("All agents active and in good standing.")

    overview = "### Cluster Overview\n" + "\n".join(lines)
    overview += "\n\n### Lifecycle Suggestions\n" + "\n".join(f"- {s}" for s in suggestions)
    return overview
