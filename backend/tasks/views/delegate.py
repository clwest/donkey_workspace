from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import Assistant, TaskAssignment


class TaskDelegateView(APIView):
    def post(self, request, assistant_id):
        assistant = get_object_or_404(Assistant, pk=assistant_id)
        task_desc = request.data["task_description"]
        target_id = request.data["target_assistant_id"]
        target = get_object_or_404(Assistant, pk=target_id)
        assignment = TaskAssignment.objects.create(
            from_assistant=assistant,
            to_assistant=target,
            description=task_desc,
        )
        return Response({"assignment_id": str(assignment.id)})
