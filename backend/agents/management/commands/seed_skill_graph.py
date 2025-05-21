from django.core.management.base import BaseCommand
from agents.models import Agent, AgentSkill, AgentSkillLink
from embeddings.helpers.helpers_io import save_embedding
import random

SKILLS = [
    {
        "name": "data analysis",
        "description": "Analyze structured and unstructured data sets to derive insights",
        "related": ["data extraction", "statistics"],
    },
    {
        "name": "code summarization",
        "description": "Summarize codebases or snippets into concise explanations",
        "related": ["debugging", "documentation"],
    },
    {
        "name": "project planning",
        "description": "Break down objectives into tasks and timelines",
        "related": ["narrative synthesis", "task breakdown"],
    },
    {
        "name": "reflection",
        "description": "Review previous work and extract lessons",
        "related": ["chain-of-thought reasoning", "memory management"],
    },
    {
        "name": "chain-of-thought reasoning",
        "description": "Reason through problems step by step",
        "related": ["reflection", "logic"],
    },
    {
        "name": "data extraction",
        "description": "Pull useful text or tables from files and PDFs",
        "related": ["data analysis"],
    },
    {
        "name": "debugging",
        "description": "Identify and fix issues in code",
        "related": ["code summarization"],
    },
    {
        "name": "open source research",
        "description": "Discover and evaluate open source tools and repos",
        "related": ["code summarization", "project planning"],
    },
    {
        "name": "memory management",
        "description": "Organize and curate long term memory",
        "related": ["reflection"],
    },
    {
        "name": "narrative synthesis",
        "description": "Combine information into coherent stories or reports",
        "related": ["project planning"],
    },
]

class Command(BaseCommand):
    help = "Seed common skills and link demo agents"

    def handle(self, *args, **options):
        skill_objs = {}
        for entry in SKILLS:
            skill, _ = AgentSkill.objects.get_or_create(
                name=entry["name"],
                defaults={
                    "description": entry.get("description", ""),
                    "embedding": [0.0] * 1536,
                },
            )
            skill_objs[entry["name"]] = skill
            if not skill.embedding:
                skill.embedding = [0.0] * 1536
                skill.save()
            save_embedding(skill, skill.embedding)

        # link related skills
        for entry in SKILLS:
            skill = skill_objs[entry["name"]]
            related = [skill_objs[r] for r in entry.get("related", []) if r in skill_objs]
            if related:
                skill.related_skills.add(*related)

        agents = Agent.objects.filter(is_demo=True)
        if not agents.exists():
            agents = Agent.objects.all()[:3]
        for agent in agents:
            chosen = random.sample(list(skill_objs.values()), k=min(3, len(skill_objs)))
            for skill in chosen:
                AgentSkillLink.objects.get_or_create(
                    agent=agent,
                    skill=skill,
                    defaults={"source": "seed", "strength": 0.6},
                )

        # print summary table
        header = f"{'Skill':20} {'Related':30} Agents"
        self.stdout.write(header)
        self.stdout.write("-" * len(header))
        for skill in skill_objs.values():
            related_names = ", ".join(skill.related_skills.values_list("name", flat=True))
            agent_names = ", ".join(
                Agent.objects.filter(agentskilllink__skill=skill).values_list("name", flat=True)
            )
            line = f"{skill.name:20} {related_names:30} {agent_names}"
            self.stdout.write(line)

        self.stdout.write(self.style.SUCCESS("Skill graph seeded."))
