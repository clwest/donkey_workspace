from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import (
    MemoryProjectionFrame,
    BeliefNarrativeWalkthrough,
    DreamframePlaybackSegment,
)
from ..serializers import (
    MemoryProjectionFrameSerializer,
    BeliefNarrativeWalkthroughSerializer,
    DreamframePlaybackSegmentSerializer,
)


@api_view(["GET", "POST"])
def memory_projection_frames(request):
    if request.method == "GET":
        frames = MemoryProjectionFrame.objects.all().order_by("-created_at")
        return Response(MemoryProjectionFrameSerializer(frames, many=True).data)

    serializer = MemoryProjectionFrameSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    frame = serializer.save()
    return Response(MemoryProjectionFrameSerializer(frame).data, status=201)


@api_view(["GET", "POST"])
def belief_walkthroughs(request):
    if request.method == "GET":
        walks = BeliefNarrativeWalkthrough.objects.all().order_by("-created_at")
        return Response(BeliefNarrativeWalkthroughSerializer(walks, many=True).data)

    serializer = BeliefNarrativeWalkthroughSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    walk = serializer.save()
    return Response(BeliefNarrativeWalkthroughSerializer(walk).data, status=201)


@api_view(["GET", "POST"])
def dreamframes(request):
    if request.method == "GET":
        segments = DreamframePlaybackSegment.objects.all().order_by("-created_at")
        return Response(DreamframePlaybackSegmentSerializer(segments, many=True).data)

    serializer = DreamframePlaybackSegmentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    seg = serializer.save()
    return Response(DreamframePlaybackSegmentSerializer(seg).data, status=201)

