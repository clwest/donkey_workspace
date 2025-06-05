import os
from intel_core.management.commands.fix_doc_progress import Command as FixCommand
from intel_core.models import Document
from utils.logging_utils import get_logger

logger = get_logger(__name__)


def repair_progress(document=None, document_id=None):
    """Repair DocumentProgress records for a single document."""
    if document == "all" or document_id == "all":
        logger.warning(
            "\u26d4\ufe0f Invalid use of 'all' in repair_progress \u2014 this is only supported via CLI."
        )
        return None

    try:
        if document_id:
            document = Document.objects.get(id=document_id)
        elif not document:
            logger.warning(
                "\u26a0\ufe0f repair_progress called without a valid document or document_id."
            )
            return None
    except Document.DoesNotExist:
        logger.warning(f"\u274c Document not found for repair: {document_id}")
        return None

    cmd = FixCommand()
    cmd.stdout = open(os.devnull, "w")
    cmd.stderr = open(os.devnull, "w")
    # Use the actual wrench emoji instead of a surrogate pair to avoid
    # UnicodeEncodeError when logging on some systems.
    logger.info(f"\U0001F527 Repairing document progress for: {document.title}")
    return cmd.handle(doc_id=str(document.id), repair=True)
