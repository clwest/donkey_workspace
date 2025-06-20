from django.utils import timezone
from accounts.models import UserOnboardingProgress
from .config import STEPS, ONBOARDING_WORLD
from prompts.utils.openai_utils import complete_chat

GUIDE_SYSTEM_PROMPT = (
    "You are the MythOS onboarding guide. Explain glossary growth, assistant "
    "skills, mythpath, and reflection loops in simple, supportive language."
)


def record_step_completion(user, step):
    if step not in STEPS:
        return None
    obj, _ = UserOnboardingProgress.objects.get_or_create(user=user, step=step)
    obj.status = "completed"
    obj.completed_at = timezone.now()
    obj.save()
    return obj


def get_onboarding_status(user):
    progress_map = {
        p.step: p.status for p in UserOnboardingProgress.objects.filter(user=user)
    }
    node_map = {n["slug"]: n for n in ONBOARDING_WORLD["nodes"]}
    return [
        {
            "step": s,
            "status": progress_map.get(s, "pending"),
            "ui_label": node_map.get(s, {}).get("ui_label"),
            "tooltip": node_map.get(s, {}).get("tooltip"),
        }
        for s in STEPS
    ]


def get_next_onboarding_step(user):
    for entry in get_onboarding_status(user):
        if entry["status"] != "completed":
            return entry["step"]
    return None


def get_progress_percent(user):
    status = get_onboarding_status(user)
    completed = sum(1 for s in status if s["status"] == "completed")
    return int((completed / len(status)) * 100)


def generate_guide_reply(message: str, hint_status: dict | None = None) -> str:
    """Return a guide response via the default model with hint context."""
    system = GUIDE_SYSTEM_PROMPT
    if hint_status:
        pairs = ", ".join(f"{k}:{v}" for k, v in hint_status.items())
        system += f" Hint status: {pairs}."
    return complete_chat(system=system, user=message, model="gpt-4o", max_tokens=250)


def get_alias_map(theme: str) -> dict:
    """Return a mapping of step slug -> alias label for the given theme."""
    alias_map = {}
    for node in ONBOARDING_WORLD["nodes"]:
        aliases = node.get("aliases", {})
        if theme in aliases:
            alias_map[node["slug"]] = aliases[theme]
    return alias_map
