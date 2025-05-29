# images/debugger.py

"""Debug utilities for inspecting prompt helpers."""

# Import models and serializers from the images app directly. When this module
# lived inside ``images`` these were relative imports, but ``sandbox`` does not
# contain its own models.  Absolute imports ensure the debugger works even when
# ``sandbox`` is optional.
from images.models import PromptHelper, PromptPlacement
from images.serializers import PromptHelperSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def debug_prompts(request):
    """
    Returns all PromptHelpers with their placement types (if any).
    Useful for inspecting current database values for prompt debugging/testing.
    """
    prompts = PromptHelper.objects.all().order_by("name")
    result = []
    for prompt in prompts:
        placements = PromptPlacement.objects.filter(name=prompt.name)
        result.append(
            {
                "id": prompt.id,
                "name": prompt.name,
                "prompt": prompt.prompt,
                "negative_prompt": prompt.negative_prompt,
                "category": prompt.category,
                "tags": prompt.tags,
                "placement": [
                    {
                        "type": p.prompt_type,
                        "placement": p.placement,
                        "enabled": p.is_enabled,
                    }
                    for p in placements
                ],
            }
        )
    return Response({"results": result})
