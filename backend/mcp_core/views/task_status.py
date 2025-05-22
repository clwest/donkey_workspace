from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from celery.result import AsyncResult


class TaskStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, task_id):
        result = AsyncResult(task_id)
        data = {
            "task_id": task_id,
            "status": result.status,
        }
        if result.status == "SUCCESS":
            data["result"] = result.result
        return Response(data)
