from django.utils import timezone
from accounts.models import UserOnboardingProgress

STEPS = ["mythpath", "world", "archetype", "summon", "wizard", "ritual"]


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
    return [
        {"step": s, "status": progress_map.get(s, "pending")}
        for s in STEPS
    ]
