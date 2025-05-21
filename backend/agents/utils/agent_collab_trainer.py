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
