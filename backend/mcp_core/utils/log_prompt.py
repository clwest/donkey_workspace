# mcp_core/utils/log_prompt.py

import logging
from typing import Optional

from mcp_core.models import PromptUsageLog, User
from prompts.models import Prompt, PromptUsageTemplate

logger = logging.getLogger(__name__)


def log_prompt_usage(
    *,
    prompt_slug: Optional[str] = None,
    prompt_title: Optional[str] = None,
    used_by: Optional[str] = None,
    purpose: Optional[str] = None,
    context_id: Optional[str] = None,
    input_context: Optional[str] = None,
    rendered_prompt: Optional[str] = None,
    result_output: Optional[str] = None,
    assistant_id: Optional[str] = None,
    assistant_slug: Optional[str] = None,
    created_by: Optional[User] = None,
    prompt: Optional[Prompt] = None,
    template: Optional[PromptUsageTemplate] = None,
    extra_data: Optional[dict] = None,
    verbose: bool = False,
) -> Optional[PromptUsageLog]:
    """Record usage of a prompt and create a ``PromptUsageLog`` entry.

    When ``verbose`` is ``True`` a short summary dictionary of the log is
    returned instead of the model instance. Any exception is logged and
    ``None`` is returned. Arbitrary ``extra_data`` can be stored on the
    ``PromptUsageLog`` for later analysis.
    """
    
    if not prompt and not prompt_slug:
        logger.warning("🛑 log_prompt_usage called without a prompt or slug")
        return None

    # Try to resolve the Prompt from slug if not passed directly
    placeholder_created = False
    if not prompt and prompt_slug:
        try:
            prompt = Prompt.objects.get(slug=prompt_slug)
        except Prompt.DoesNotExist:
            logger.warning(
                "[PromptUsage] missing slug=%s; creating placeholder", prompt_slug
            )
            prompt, _ = Prompt.objects.get_or_create(
                slug=prompt_slug,
                defaults={
                    "title": prompt_title or prompt_slug.replace("-", " ").title(),
                    "type": "system",
                    "content": rendered_prompt or "",
                    "source": "auto",
                },
            )
            placeholder_created = True

    # Determine fallback title and slug
    final_slug = prompt_slug or (prompt.slug if prompt else "unknown")
    final_title = prompt_title or (prompt.title if prompt else "Untitled")

    try:
        log = PromptUsageLog.objects.create(
            prompt_slug=final_slug,
            prompt_title=final_title,
            used_by=used_by or "unspecified",
            purpose=purpose,
            context_id=str(context_id) if context_id else None,
            input_context=input_context or "",
            rendered_prompt=rendered_prompt or "",
            result_output=result_output or "",
            assistant_id=assistant_id,
            created_by=created_by,
            prompt=prompt,
            template=template,
            extra_data=extra_data or {},
        )

        logger.info(
            "[PromptUsage] assistant=%s prompt=%s fallback=%s",
            assistant_slug or assistant_id,
            final_slug,
            placeholder_created,
        )

        if verbose:
            return {
                "log_id": str(log.id),
                "summary": f"📦 Logged prompt `{final_title}` used by `{used_by or 'unknown'}`",
                "timestamp": str(log.created_at),
            }
        return log

    except Exception as e:
        logger.error(f"❌ Failed to log prompt usage: {e}", exc_info=True)
        return None
