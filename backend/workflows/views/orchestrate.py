from rest_framework.views import APIView
from rest_framework.response import Response
# Import models from the parent workflows package rather than the views package
# to avoid incorrect module paths like ``workflows.views.models`` which can
# cause ``ModuleNotFoundError`` when Django imports the URL configuration.
from ..models import WorkflowDefinition, WorkflowExecutionLog


class WorkflowOrchestrateView(APIView):
    def post(self, request):
        definition_id = request.data["workflow_definition_id"]
        definition = WorkflowDefinition.objects.get(pk=definition_id)
        execution = WorkflowExecutionLog.objects.create(
            workflow=definition, status="pending"
        )
        return Response({"execution_id": execution.id})
