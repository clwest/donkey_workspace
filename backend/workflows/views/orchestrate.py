from rest_framework.views import APIView
from rest_framework.response import Response

# Import models from the parent workflows package rather than the views package
# to avoid incorrect module paths like ``workflows.views.models`` which can
# cause ``ModuleNotFoundError`` when Django imports the URL configuration.
from ..models import WorkflowDefinition, WorkflowExecutionLog
from assistants.models import Assistant


class WorkflowOrchestrateView(APIView):
    def post(self, request):
        definition_id = request.data["workflow_definition_id"]
        definition = WorkflowDefinition.objects.get(pk=definition_id)
        triggered_by_id = request.data.get("triggered_by_id")
        if triggered_by_id:
            from utils.resolvers import resolve_or_error
            from django.core.exceptions import ObjectDoesNotExist

            try:
                triggered_by = resolve_or_error(triggered_by_id, Assistant)
            except ObjectDoesNotExist:
                triggered_by = None
        else:
            triggered_by = None
        execution = WorkflowExecutionLog.objects.create(
            workflow=definition,
            triggered_by=triggered_by,
            execution_data={},
            outcome_summary="",
            status="pending",
        )
        return Response({"execution_id": execution.id})
