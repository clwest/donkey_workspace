from django.core.management.base import BaseCommand
from memory.models import MemoryEntry
from mcp_core.models import MemoryContext
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from embeddings.helpers.helpers_processing import generate_embedding
from embeddings.helpers.helpers_io import save_embedding
from django.utils.text import slugify
import json

class Command(BaseCommand):
    help = "Group recent memory reflections and embed the summaries."

    def handle(self, *args, **options):
        print("🔍 Fetching recent reflection entries...")

        recent_reflections = MemoryEntry.objects.filter(
            type="reflection_summary"
        ).order_by("-created_at")[:50]

        if not recent_reflections.exists():
            print("⚠️ No recent reflections found.")
            return

        chunks = []
        for entry in recent_reflections:
            chunks.append(f"- {entry.summary}\n{entry.event[:300]}...")

        prompt = f"""
You are an assistant organizing internal memory reflections.

Group the following reflections into themes and provide one unified summary for each group.
Return the result as a list of 3-7 group objects in JSON format.
Each object should include:
- title: the group theme or insight
- summary: what this group of reflections is about
- source_summaries: a list of the original summaries being grouped

Reflections:
{chr(10).join(chunks)}
        """

        print("🤖 Calling GPT-4 to generate grouped reflection summary...")
        engine = AssistantReflectionEngine.get_reflection_assistant()
        response = engine.call_gpt4(prompt)

        if not response:
            print("❌ No response from LLM.")
            return

        try:
            json_data = json.loads(response)
        except json.JSONDecodeError:
            print("🧨 Failed to parse LLM response as JSON.")
            return

        print("🧠 Storing grouped reflections with embeddings...")
        count = 0
        for group in json_data:
            summary = group.get("summary")
            if not summary:
                continue

            embedding = generate_embedding(summary)
            if not embedding:
                print(f"⚠️ Failed to embed: {summary[:50]}...")
                continue

            ctx = MemoryContext.objects.create(
                title=group.get("title")[:100],
                summary=summary,
                content=json.dumps(group, indent=2),
                slug=slugify(group.get("title")),
            )

            save_embedding(ctx, embedding)
            print(f"✅ Saved: {ctx.title}")
            count += 1

        print("\n🎉 Done!")
        print(f"✔️ Grouped and embedded: {count}")
