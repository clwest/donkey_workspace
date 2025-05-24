from django.utils.deprecation import MiddlewareMixin
from .models.reflection import AssistantReflectionLog
from simulation.models import PromptCascadeLog, CascadeNodeLink


class ReflectionCascadeMiddleware(MiddlewareMixin):
    """Log cascade information when reflections occur."""

    def process_response(self, request, response):
        prompt_id = request.headers.get("X-Prompt-ID")
        assistant_id = response.headers.get("X-Assistant-ID")
        if getattr(request, "reflection_logged", False) and prompt_id:
            cascade, _ = PromptCascadeLog.objects.get_or_create(
                prompt_id=prompt_id, defaults={"triggered_by_id": assistant_id}
            )
            CascadeNodeLink.objects.create(
                cascade=cascade,
                assistant_id=assistant_id,
            )
        return response
