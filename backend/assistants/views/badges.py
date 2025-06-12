from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import Assistant, Badge
from assistants.serializers_pass import BadgeSerializer
from assistants.utils.badge_logic import update_assistant_badges


class BadgeListView(APIView):
    def get(self, request):
        slug = request.GET.get("assistant")
        badges = Badge.objects.all()
        if slug:
            assistant = get_object_or_404(Assistant, slug=slug)
            earned = assistant.skill_badges or []
            if earned:
                badges = badges.filter(slug__in=earned)
            serializer = BadgeSerializer(
                badges, many=True, context={"assistant": assistant}
            )
            return Response(
                {
                    "assistant": assistant.slug,
                    "badges": serializer.data,
                    "history": assistant.badge_history,
                }
            )
        serializer = BadgeSerializer(badges, many=True)
        return Response(serializer.data)


class AssistantBadgesView(APIView):
    def get(self, request, slug):
        assistant = get_object_or_404(Assistant, slug=slug)
        all_badges = list(Badge.objects.values_list("slug", flat=True))
        current = assistant.skill_badges or []
        remaining = [b for b in all_badges if b not in current]
        next_badge = remaining[0] if remaining else None
        return Response(
            {
                "current": current,
                "possible": all_badges,
                "next": next_badge,
            }
        )

    def post(self, request, slug):
        assistant = get_object_or_404(Assistant, slug=slug)
        badges = request.data.get("badges")
        primary = request.data.get("primary_badge")
        override = bool(request.data.get("override"))
        manual = None
        if isinstance(badges, list):
            current = set(assistant.skill_badges or [])
            manual = {b: True for b in badges}
            for b in current:
                if b not in badges:
                    manual[b] = False

        update_assistant_badges(assistant, manual=manual, override=override)
        if primary is not None:
            assistant.primary_badge = primary or None
            assistant.save(update_fields=["primary_badge"])
        assistant.refresh_from_db()
        return Response(
            {
                "updated": assistant.skill_badges,
                "primary_badge": assistant.primary_badge,
            }
        )


class AssistantBadgeProgressView(APIView):
    """Return badge progress information for an assistant."""

    def get(self, request, slug):
        assistant = get_object_or_404(Assistant, slug=slug)
        badges = Badge.objects.all()
        serializer = BadgeSerializer(
            badges, many=True, context={"assistant": assistant}
        )
        return Response(
            {
                "assistant": assistant.slug,
                "badges": serializer.data,
                "history": assistant.badge_history,
            }
        )
