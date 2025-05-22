from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from assistants.models import Assistant
from intel_core.models import Document


class SubAssistantCreateView(APIView):
    def post(self, request, assistant_id):
        parent = get_object_or_404(Assistant, pk=assistant_id)
        doc_ids = request.data.get("document_ids", [])
        docs = Document.objects.filter(id__in=doc_ids)
        preset_name = docs[0].title if docs else "Sub"
        preset_specialty = ", ".join(d.title for d in docs)
        sub = Assistant.objects.create(
            name=f"{parent.name} – {preset_name}",
            parent_assistant=parent,
            specialty=preset_specialty,
        )
        if docs:
            sub.documents.set(docs)
        return Response({"sub_assistant_id": str(sub.id)}, status=status.HTTP_200_OK)
