from celery import shared_task
import subprocess
from assistants.models import AssistantCommandLog, Assistant

@shared_task
def run_cli_command_task(log_id: int, command: str, flags=None, assistant_slug=None):
    flags = flags or []
    log = AssistantCommandLog.objects.get(id=log_id)
    if assistant_slug and not log.assistant_id:
        log.assistant = Assistant.objects.filter(slug=assistant_slug).first()
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
    return log.id
