from django.utils.text import slugify
from django.contrib.auth import get_user_model
from prompts.models import Prompt
from assistants.models.assistant import Assistant
from assistants.models.project import AssistantProject, AssistantMemoryChain
from assistants.services import AssistantService
from project.models import ProjectType, ProjectStatus

PRIMARY_PROMPT = (
    "You are the Primary Assistant in a multi-agent intelligence system. "
    "Your role is to coordinate memory, reflections, objectives, and agent activity. "
    "You spawn delegated assistants for specialized tasks when memory or context exceeds manageable limits. "
    "You maintain long-term awareness, ask clarifying questions when needed, and provide continuity across assistant interactions."
)


def prompt_to_assistant(name: str, tone: str, personality: str) -> Assistant:
    """Create an assistant from a predefined system prompt."""
    prompt, _ = Prompt.objects.get_or_create(
        title=f"{name} System Prompt",
        defaults={
            "content": PRIMARY_PROMPT,
            "type": "system",
            "source": "seed_primary_assistant",
            "tone": tone,
            "token_count": len(PRIMARY_PROMPT.split()),
        },
    )

    assistant, created = Assistant.objects.get_or_create(
        slug=slugify(name),
        defaults={
            "name": name,
            "tone": tone,
            "personality": personality,
            "specialty": "orchestration",
            "system_prompt": prompt,
            "is_primary": True,
            "traits": ["strategic", "humorous"],
            "persona_mode": "planner",
        },
    )

    if created:
        project = AssistantProject.objects.create(
            assistant=assistant,
            title="Primary Orchestration",
            goal="Coordinate all assistants and maintain memory continuity.",
            status="active",
        )

        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username="seed_user",
            defaults={"email": "seed@example.com", "password": "notsecure"},
        )

        core_project = AssistantService.create_project(
            user=user,
            title="Primary Orchestration",
            assistant=assistant,
            assistant_project=project,
            project_type=ProjectType.ASSISTANT,
            status=ProjectStatus.ACTIVE,
        )

        chain = AssistantMemoryChain.objects.create(
            project=core_project,
            title="Global Memory Chain",
            description="Auto mode chain for system-level memory.",
            mode="automatic",
        )
        assistant.default_memory_chain = chain
        assistant.save(update_fields=["default_memory_chain"])

    return assistant
