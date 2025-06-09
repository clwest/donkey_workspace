import json
import logging
from django.utils import timezone
from django.conf import settings
import redis

from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from assistants.models.assistant import AssistantDriftRefinementLog

REDIS_URL = getattr(settings, "REDIS_URL", "redis://127.0.0.1:6379/1")
r = redis.Redis.from_url(REDIS_URL)

TRUST_CACHE_PREFIX = "assistant:trust:"  # redis key prefix
logger = logging.getLogger(__name__)


def get_cached_trust(slug: str) -> dict | None:
    raw = r.get(f"{TRUST_CACHE_PREFIX}{slug}")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def set_cached_trust(slug: str, data: dict, ttl: int = 3600):
    try:
        r.setex(f"{TRUST_CACHE_PREFIX}{slug}", ttl, json.dumps(data))
    except Exception:
        logger.warning("failed to cache trust", extra={"slug": slug})


def compute_trust_score(assistant: Assistant) -> dict:
    """Return trust data dict with score and level."""
    badge_count = len(assistant.skill_badges or [])
    glossary = float(assistant.glossary_score or 0)
    week = timezone.now() - timezone.timedelta(days=7)
    reflections = AssistantReflectionLog.objects.filter(
        assistant=assistant, created_at__gte=week
    ).count()
    drift_fixes = AssistantDriftRefinementLog.objects.filter(
        assistant=assistant, created_at__gte=week
    ).count()

    score = glossary * 0.4 + min(badge_count, 10) * 3
    score += min(reflections, 10) * 4
    score -= drift_fixes * 2
    score = max(0, min(100, int(round(score))))

    if score >= 80:
        level = "ready"
    elif score >= 50:
        level = "training"
    else:
        level = "needs_attention"

    return {
        "score": score,
        "level": level,
        "components": {
            "badge_count": badge_count,
            "glossary_match_pct": glossary,
            "reflections_last_7d": reflections,
            "drift_fixes_recent": drift_fixes,
        },
    }


def update_assistant_trust_cache(assistant: Assistant) -> dict:
    data = compute_trust_score(assistant)
    set_cached_trust(assistant.slug, data)
    return data


class TrustProfileMixin:
    @property
    def trust_score(self) -> int:
        cached = get_cached_trust(self.slug)
        if cached:
            return cached.get("score", 0)
        data = update_assistant_trust_cache(self)
        return data["score"]

    @property
    def trust_level(self) -> str:
        cached = get_cached_trust(self.slug)
        if cached:
            return cached.get("level", "training")
        data = update_assistant_trust_cache(self)
        return data["level"]
