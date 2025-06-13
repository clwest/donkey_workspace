from celery import shared_task
import subprocess
from assistants.models import AssistantCommandLog, Assistant
from utils.resolvers import resolve_or_error
from django.core.exceptions import ObjectDoesNotExist


@shared_task
def run_cli_command_task(log_id: int, command: str, flags=None, assistant_slug=None):
    flags = flags or []
    log = AssistantCommandLog.objects.get(id=log_id)
    if assistant_slug and not log.assistant_id:
        try:
            log.assistant = resolve_or_error(assistant_slug, Assistant)
        except ObjectDoesNotExist:
            log.assistant = None
        if log.assistant:
            log.save(update_fields=["assistant"])
    if flags and not log.flags:
        log.flags = " ".join(flags)
        log.save(update_fields=["flags"])
    proc = subprocess.Popen(
        ["python", "manage.py", command, *flags],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    output, _ = proc.communicate()
    log.output = output
    log.status = "success" if proc.returncode == 0 else "error"
    log.save(update_fields=["output", "status"])
    if log.status == "success" and log.assistant_id:
        reflect_on_cli_log.delay(log.id)
    return log.id


@shared_task
def reflect_on_cli_log(log_id: int) -> int:
    """Trigger reflection summarizing a CLI command log."""
    log = (
        AssistantCommandLog.objects.filter(id=log_id)
        .select_related("assistant")
        .first()
    )
    if not log or not log.assistant_id:
        return log_id
    from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine

    engine = AssistantReflectionEngine(log.assistant)
    title = f"CLI command: {log.command}"
    summary = log.output[:400] if log.output else ""
    AssistantReflectionEngine.get_or_create_project(log.assistant)
    try:
        engine.reflect_now(scene=title, location_context=summary)
    except Exception:
        pass
    return log_id
