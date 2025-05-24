from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
import uuid
import os

from intel_core.models import JobStatus
from intel_core.tasks import (
    process_url_upload,
    process_video_upload,
    process_pdf_upload,
)


class DocumentImportView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES.get("file")
        url = request.data.get("url")
        video = request.data.get("video")
        session_id = request.data.get("session_id") or uuid.uuid4()
        job = JobStatus.objects.create(status="queued", session_id=session_id)
        job_id = str(job.job_id)

        if file_obj:
            path = default_storage.save(file_obj.name, file_obj)
            full_path = os.path.join(settings.MEDIA_ROOT, path)
            process_pdf_upload.delay([full_path], job_id=job_id, session_id=str(session_id))
        elif url:
            process_url_upload.delay([url], job_id=job_id, session_id=str(session_id))
        elif video:
            process_video_upload.delay([video], job_id=job_id, session_id=str(session_id))
        else:
            return Response({"error": "No file or url provided"}, status=400)

        return Response({"job_id": job_id, "session_id": str(session_id)}, status=status.HTTP_200_OK)


class UploadStatusView(APIView):
    def get(self, request, session_id):
        try:
            job = JobStatus.objects.get(session_id=session_id)
        except JobStatus.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        data = {
            "stage": job.stage,
            "percent_complete": job.progress,
            "current_chunk": job.current_chunk,
            "total_chunks": job.total_chunks,
        }
        return Response(data)
