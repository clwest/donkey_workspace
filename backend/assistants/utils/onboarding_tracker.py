from django.utils import timezone
from accounts.models import UserOnboardingProgress
from onboarding.config import STEPS, ONBOARDING_WORLD


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
