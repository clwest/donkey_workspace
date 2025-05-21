def simulate_agent_skill_conversation(teacher, learner, skill):
    """Simulates a short skill explanation conversation."""
    from openai import OpenAI
    from agents.models import AgentFeedbackLog, AgentTrainingAssignment
    from intel_core.models import Document

    client = OpenAI()
    prompt = (
        f"Write a brief conversation where {teacher.name} teaches the skill \"{skill.name}\" to {learner.name}. "
        "Use 2-3 exchanges. Format each line as **Speaker**: message."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=300,
        )
        transcript = response.choices[0].message.content.strip()
    except Exception as e:
        transcript = f"**{teacher.name}**: Sorry, failed to simulate conversation ({e})."

    AgentFeedbackLog.objects.create(
        agent=learner,
        feedback_text=f"{teacher.name} taught {skill.name}.\n{transcript}",
        feedback_type="collab",
    )

    lowered = transcript.lower()
    if "follow" in lowered or "more" in lowered:
        doc = Document.objects.order_by("?").first()
        if doc:
            AgentTrainingAssignment.objects.create(
                agent=learner,
                assistant=learner.parent_assistant or teacher.parent_assistant,
                document=doc,
            )

    return transcript


def run_simulated_skill_transfer_if_gap(agent, required_skill):
    """If agent lacks skill, simulate peer mentoring and log result."""
    from agents.models import AgentSkill, AgentSkillLink, AgentFeedbackLog
    from memory.models import MemoryEntry
    from django.contrib.contenttypes.models import ContentType

    skill_name = required_skill.lower()
    current = {s.lower() for s in agent.skills or []}
    verified = {(
        s.get("skill") if isinstance(s, dict) else str(s)
    ).lower() for s in agent.verified_skills or []}
    if skill_name in current or skill_name in verified:
        return None

    skill = AgentSkill.objects.filter(name__iexact=required_skill).first()
    if not skill:
        return None

    link = (
        AgentSkillLink.objects.filter(skill=skill)
        .exclude(agent=agent)
        .order_by("-strength")
        .select_related("agent")
        .first()
    )
    if not link:
        return None

    peer = link.agent
    transcript = simulate_agent_skill_conversation(peer, agent, skill)

    memory = MemoryEntry.objects.create(
        event=f"{peer.name} mentored {agent.name} on {skill.name}.",
        assistant=agent.parent_assistant,
        source_role="system",
        linked_content_type=ContentType.objects.get_for_model(agent.__class__),
        linked_object_id=agent.id,
        full_transcript=transcript,
    )

    AgentFeedbackLog.objects.create(
        agent=agent,
        feedback_text=f"Peer training on {skill.name} by {peer.name}",
        feedback_type="training",
    )

    return memory
