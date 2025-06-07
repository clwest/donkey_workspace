from ..models import GlossaryKeeperLog

__all__ = ["get_latest_keeper_logs"]


def get_latest_keeper_logs(limit: int = 25):
    """Return latest keeper logs ordered by timestamp."""
    return GlossaryKeeperLog.objects.select_related("anchor", "assistant").order_by(
        "-timestamp"
    )[:limit]
