from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count
from assistants.models import Assistant

class SystemSummaryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        total = Assistant.objects.count()
        top_badge = (
            Assistant.objects.exclude(primary_badge__isnull=True)
            .values("primary_badge")
            .annotate(c=Count("id"))
            .order_by("-c")
            .first()
        )
        return Response(
            {
                "assistant_count": total,
                "most_common_badge": top_badge["primary_badge"] if top_badge else None,
            }
        )
