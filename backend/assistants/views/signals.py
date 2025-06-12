from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from assistants.models.assistant import SignalSource, SignalCatch
from assistants.serializers_pass import SignalSourceSerializer, SignalCatchSerializer


@api_view(["GET", "POST"])
def signal_sources(request):
    if request.method == "GET":
        sources = SignalSource.objects.all().order_by("-priority", "name")
        serializer = SignalSourceSerializer(sources, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        serializer = SignalSourceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def signal_catches(request):
    catches = SignalCatch.objects.all().order_by("-created_at")
    serializer = SignalCatchSerializer(catches, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def create_signal_catch(request):
    serializer = SignalCatchSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def update_signal_catch(request, pk):
    try:
        catch = SignalCatch.objects.get(pk=pk)
    except SignalCatch.DoesNotExist:
        return Response(
            {"error": "Signal catch not found."}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = SignalCatchSerializer(catch, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
