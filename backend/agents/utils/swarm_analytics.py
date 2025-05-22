from datetime import datetime, timedelta
from django.db.models import Count
from django.utils import timezone

from agents.models.core import (
    Agent,
    AgentCluster,
    AgentSkillLink,
    AgentFeedbackLog,
)
from agents.models.lore import (
    AgentLegacy,
    SwarmMemoryEntry
)
from assistants.models.assistant import AssistantCouncil
from assistants.models.reflection import AssistantReflectionLog
from assistants.models.project import AssistantProject
from django.db.models import Avg
from django.db.models.functions import Length
from mcp_core.models import Tag


def get_season_marker(date: datetime) -> str:
    """Return the season tag for a given date."""
    month = date.month
    if month in [3, 4, 5]:
        return "spring"
    if month in [6, 7, 8]:
        return "summer"
    if month in [9, 10, 11]:
        return "fall"
    return "winter"


def get_swarm_snapshot(date: datetime):
    """Retrieve agents, clusters and memories active up to a given date."""
    return {
        "agents": Agent.objects.filter(created_at__lte=date),
        "clusters": AgentCluster.objects.filter(created_at__lte=date),
        "memories": SwarmMemoryEntry.objects.filter(created_at__lte=date),
    }


def generate_temporal_swarm_report() -> dict:
    """Returns stats and insights over time."""
    now = timezone.now()
    windows = {
        "7d": now - timedelta(days=7),
        "30d": now - timedelta(days=30),
        "90d": now - timedelta(days=90),
    }

    report: dict[str, dict] = {}
    for label, start in windows.items():
        created = Agent.objects.filter(created_at__gte=start).count()
        archived = Agent.objects.filter(is_active=False, updated_at__gte=start).count()
        resurrected = Agent.objects.filter(reactivated_at__gte=start).count()

        gained_qs = (
            AgentSkillLink.objects.filter(created_at__gte=start)
            .values("skill__name")
            .annotate(c=Count("id"))
            .order_by("-c")[:5]
        )
        gained = [
            f"{d['skill__name']} ({d['c']})" for d in gained_qs if d["skill__name"]
        ]

        clusters_created = AgentCluster.objects.filter(created_at__gte=start).count()
        clusters_archived = AgentCluster.objects.filter(
            is_active=False, updated_at__gte=start
        ).count()

        report[label] = {
            "agents_created": created,
            "agents_archived": archived,
            "agents_resurrected": resurrected,
            "top_skills_gained": gained,
            "cluster_churn": {
                "created": clusters_created,
                "archived": clusters_archived,
            },
        }

    trending_tags = (
        SwarmMemoryEntry.objects.filter(created_at__gte=windows["90d"])
        .values("tags__name")
        .annotate(c=Count("id"))
        .order_by("-c")[:5]
    )
    forecasted_skills = [t["tags__name"] for t in trending_tags if t["tags__name"]]

    report["forecasted_skills"] = forecasted_skills
    return report


def evaluate_cluster_health(cluster: AgentCluster) -> dict:
    """Return basic health metrics and store a summary log."""

    total = cluster.agents.count()
    active = cluster.agents.filter(is_active=True).count()
    activity_ratio = active / total if total else 0.0

    skills = set()
    for agent in cluster.agents.all():
        skills.update([s.lower() for s in getattr(agent, "skills", [])])

    task_count = 0
    if cluster.project_id:
        task_count = cluster.project.tasks.filter(status="pending").count()
    skill_coverage = len(skills) / float(task_count or 1)

    feedback_logs = AgentFeedbackLog.objects.filter(agent__in=cluster.agents.all())
    pos = feedback_logs.filter(score__gte=0.5).count()
    neg = feedback_logs.filter(score__lte=0.0).count()
    total_logs = feedback_logs.count()
    sentiment = {
        "positive": pos,
        "negative": neg,
        "neutral": total_logs - pos - neg,
    }

    viability = 0.25 * activity_ratio
    viability += 0.25 * min(skill_coverage, 1.0)
    viability += 0.5 * (pos / total_logs if total_logs else 0.5)
    viability = round(min(viability, 1.0), 2)

    summary = (
        f"Activity {activity_ratio:.2f}; coverage {skill_coverage:.2f}; "
        f"+{pos}/-{neg} feedback; viability {viability:.2f}"
    )
    entry = SwarmMemoryEntry.objects.create(
        title=f"Cluster Health: {cluster.name}",
        content=summary,
        origin="cluster_health",
    )
    entry.linked_agents.set(cluster.agents.all())

    return {
        "agent_activity_ratio": activity_ratio,
        "skill_coverage": skill_coverage,
        "feedback_sentiment": sentiment,
        "projected_viability": viability,
    }


def score_global_strategy() -> dict:
    """Evaluate overall strategy alignment and cohesion."""

    total_projects = AssistantProject.objects.count()
    aligned_projects = AssistantCouncil.objects.exclude(mission_node=None).count()
    alignment = aligned_projects / float(total_projects or 1)

    participation = (
        AssistantReflectionLog.objects.values("assistant_id").distinct().count()
    )

    reflection_depth = (
        AssistantReflectionLog.objects.annotate(l=Length("summary"))
        .aggregate(avg=Avg("l"))
        .get("avg")
        or 0.0
    )

    councils = AssistantCouncil.objects.all()
    total_memberships = sum(c.members.count() for c in councils) or 1
    unique_members = {a.id for c in councils for a in c.members.all()}
    cohesion = len(unique_members) / float(total_memberships)

    metrics = {
        "alignment": round(alignment, 2),
        "participation": participation,
        "reflection_depth": round(reflection_depth, 2),
        "cohesion": round(cohesion, 2),
    }

    entry = SwarmMemoryEntry.objects.create(
        title="Global Strategy Score",
        content=str(metrics),
        origin="strategy_score",
    )
    for name in ["strategy_score", "alignment", "cohesion"]:
        tag, _ = Tag.objects.get_or_create(name=name, defaults={"slug": name})
        entry.tags.add(tag)

    return metrics
