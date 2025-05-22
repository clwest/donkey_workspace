"""Memory-related service functions."""

from typing import List
from openai import OpenAI

from memory.models import MemoryEntry
from assistants.models.reflection import AssistantReflectionLog
from embeddings.helpers.helpers_io import save_embedding


client = OpenAI()


def reflect_on_memory(memory_ids: List[str]) -> AssistantReflectionLog:
    """Generate a reflection log across provided memory IDs."""
    memories = MemoryEntry.objects.filter(id__in=memory_ids)
    if not memories.exists():
        raise ValueError("No valid memories found")

    combined_text = "\n\n".join([m.event for m in memories])

    prompt = f"""
    Summarize the following experiences into a coherent reflection that captures lessons learned, emotional tone, and overall patterns:

    {combined_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert in emotional intelligence and personal growth.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1024,
    )

    summary = response.choices[0].message.content.strip()

    reflection = AssistantReflectionLog.objects.create(
        summary=summary,
        time_period_start=min(m.timestamp for m in memories),
        time_period_end=max(m.timestamp for m in memories),
    )
    reflection.linked_memories.set(memories)
    save_embedding(reflection, embedding=[])
    return reflection
