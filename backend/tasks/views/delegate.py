from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models.assistant import Assistant
from assistants.models.tasks import TaskAssignment


class TaskDelegateView(APIView):
    def post(self, request, assistant_id):
        assistant = get_object_or_404(Assistant, pk=assistant_id)
        task_desc = request.data["task_description"]
        target_id = request.data["target_assistant_id"]
        required_badges = request.data.get("required_badges", [])
        target = get_object_or_404(Assistant, pk=target_id)
        missing = [b for b in required_badges if b not in target.skill_badges]
        if missing:
            return Response(
                {"error": "Target missing badges", "missing": missing}, status=400
            )
        assignment = TaskAssignment.objects.create(
            from_assistant=assistant,
            to_assistant=target,
            description=task_desc,
            required_badges=required_badges,
        )
        return Response({"assignment_id": str(assignment.id)})
