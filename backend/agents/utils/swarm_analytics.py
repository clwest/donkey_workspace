from datetime import timedelta
from django.db.models import Count
from django.utils import timezone

from agents.models import (
    Agent,
    AgentLegacy,
    AgentCluster,
    AgentSkillLink,
    AgentFeedbackLog,
    SwarmMemoryEntry,
)


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
