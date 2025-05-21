def simulate_agent_skill_conversation(teacher, learner, skill, *, thread=None):
    """Simulates a short skill explanation conversation."""
    from openai import OpenAI
    from agents.models import AgentFeedbackLog, AgentTrainingAssignment
    from intel_core.models import Document
    from memory.models import MemoryEntry
    from mcp_core.models import Tag
    from django.utils.text import slugify

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

    memory = MemoryEntry.objects.create(
        event=f"{teacher.name} taught {learner.name} {skill.name}",
        full_transcript=transcript,
        is_conversation=True,
        source_role="agent",
        narrative_thread=thread,
    )
    memory.linked_agents.set([teacher, learner])

    tag_names = ["mentoring", skill.name.lower()]
    tags = []
    for name in tag_names:
        tag, _ = Tag.objects.get_or_create(name=name, defaults={"slug": slugify(name)})
        tags.append(tag)
    memory.tags.set(tags)

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
