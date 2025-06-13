import logging
from celery import shared_task
from django.core.management import call_command

logger = logging.getLogger(__name__)


@shared_task
def run_daily_embedding_repair():
    """Run the repair_flagged_embeddings management command."""
    logger.info("🔧 Running daily embedding repair")
    call_command("repair_flagged_embeddings")
    logger.info("✅ Daily embedding repair complete")
    return "done"
