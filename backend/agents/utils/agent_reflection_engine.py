from typing import Optional, List
from mcp_core.models import MemoryContext
from utils.llm_router import call_llm
import json


class AgentReflectionEngine:
    """
    Handles retrieval and summarization of important memories
    for agent reflection processes.
    """

    def __init__(self, user: Optional = None):
        self.user = user

    def reflect_on(
        self,
        target_type: Optional[str] = None,
        since: Optional[str] = None,
        limit: int = 10,
    ) -> List[MemoryContext]:
        query = MemoryContext.objects.filter(important=True)
        if target_type:
            query = query.filter(target_type=target_type)
        if since:
            query = query.filter(created_at__gte=since)
        return list(query.order_by("-created_at")[:limit])

    def summarize_reflection(self, memories: List[MemoryContext]) -> str:
        summary = f"🧠 Reflection on {len(memories)} important memories:\n\n"
        for m in memories:
            summary += f"• [{m.target_type.upper()} ID {m.target_id}] {m.content}\n"
        return summary

    def get_llm_summary(self, memories: List[MemoryContext]) -> str:
        if not memories:
            return "No memories available to reflect upon."

        content = "\n".join([f"- {m.content}" for m in memories])
        prompt = f"""You are a thoughtful AI agent reviewing recent important memory logs.

Summarize what patterns, issues, and insights are emerging from these notes:

{content}

Respond with a short, intelligent reflection as if you're thinking aloud."""

        return call_llm(
            [{"role": "user", "content": prompt}],
            model="gpt-4o",
        )

    def get_structured_reflection(
        self, memories: List[MemoryContext], goal: Optional[str] = None
    ) -> dict:
        if not memories:
            return {
                "title": "No Memories",
                "summary": "No memories available to reflect upon.",
                "tags": [],
                "mood": "neutral",
            }

        memory_content = "\n".join([f"- {m.content}" for m in memories])
        prompt = f"""You are an expert AI reflection assistant.

Here are important memory logs:
{memory_content}

{f"Focus especially on: {goal}" if goal else "Reflect holistically on them."}

Please respond in this structured JSON format:
{{
  "title": "A short, meaningful title summarizing the main insight.",
  "summary": "A thoughtful and detailed reflection analyzing the memories.",
  "tags": ["tag1", "tag2"],
  "mood": "neutral"
}}"""

        raw = call_llm(
            [{"role": "user", "content": prompt}],
            model="gpt-4o",
        )

        try:
            parsed = json.loads(raw)
            return parsed
        except Exception as e:
            print("Error parsing structured reflection:", e)
            return {
                "title": "Reflection Error",
                "summary": "Reflection generation failed.",
                "tags": [],
                "mood": "unknown",
            }

    def analyze_mood(self, text: str) -> str:
        if not text:
            return "neutral"

        prompt = f"""
Analyze the following reflection and determine its overall mood or emotional tone in ONE WORD.

Example moods: optimistic, cautious, celebratory, concerned, anxious, neutral.

Reflection:
---
{text}
---

Respond ONLY with the single word for the mood.
"""

        return (
            call_llm(
                [{"role": "user", "content": prompt}],
                model="gpt-4o",
            )
            .strip()
            .lower()
        )

    def reflect_on_custom(self, memories: List[MemoryContext], goal: str = "") -> dict:
        if not memories:
            return {
                "title": "Empty Reflection",
                "summary": "No memories provided for reflection.",
                "tags": [],
                "mood": "unknown",
            }

        content = "\n".join([f"- {m.content}" for m in memories])
        prompt = f"""You are an AI agent asked to reflect thoughtfully on selected memories.

Here are the memories:
{content}

{f"The user's goal for this reflection is: {goal}" if goal else "No specific goal provided."}

1. Give the reflection a short, clear title.
2. Summarize patterns, insights, or next steps.
3. Suggest 3-5 relevant tags.
4. Predict the mood of the overall reflection (Positive, Neutral, Negative).

Respond in this JSON format:
{{
  "title": "Title here",
  "summary": "Summary here",
  "tags": ["tag1", "tag2"],
  "mood": "Positive"
}}
"""

        raw = call_llm(
            [{"role": "user", "content": prompt}],
            model="gpt-4o",
        )

        try:
            parsed = json.loads(raw)
            return parsed
        except Exception as e:
            print("Error parsing custom reflection:", e)
            return {
                "title": "Custom Reflection",
                "summary": "Reflection generation failed.",
                "tags": [],
                "mood": "unknown",
            }

    def expand_summary(self, old_summary: str, memories: List[MemoryContext]) -> str:
        new_memories_text = "\n".join([f"- {m.content}" for m in memories])
        prompt = f"""You previously reflected on important memories with the following summary:

"{old_summary}"

Now, additional memory logs have been selected:
{new_memories_text}

Please thoughtfully expand and improve the reflection.
Preserve the important insights from the old summary, but naturally build upon them with the new information.
Respond like a human thoughtfully thinking aloud — avoid simply repeating content."""

        return call_llm(
            [{"role": "user", "content": prompt}],
            model="gpt-4o",
        )

    def generate_reflection_title(self, raw_summary: str) -> str:
        if not raw_summary:
            return "Untitled Reflection"

        prompt = f"""You are an AI reflection assistant. Based on the following notes, generate a short, insightful title:

{raw_summary}

Respond with ONLY the title, nothing else."""

        return call_llm(
            [{"role": "user", "content": prompt}],
            model="gpt-4o",
        ).strip()

    def get_llm_summary_from_raw_summary(self, raw_summary: str) -> str:
        if not raw_summary:
            return "No raw summary provided."

        prompt = f"""You are a thoughtful AI agent reviewing a summarized collection of important memory events.

Reflect and expand on the following:

{raw_summary}

Offer a short, intelligent insight summarizing the major themes and lessons."""

        return call_llm(
            [{"role": "user", "content": prompt}],
            model="gpt-4o",
        )
