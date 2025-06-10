from django.http import JsonResponse, HttpResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST


def health(request):
    return JsonResponse({"status": "ok"})


def metrics(request):
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)
