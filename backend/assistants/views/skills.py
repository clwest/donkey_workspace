from rest_framework.views import APIView
from rest_framework.response import Response

from learning_loops.models import SkillTrainingMap, MemorySkillAlignmentIndex


class SkillPlanView(APIView):
    """Return skill training maps and memory alignment info."""

    def get(self, request, assistant_id):
        maps = SkillTrainingMap.objects.filter(assistant_id=assistant_id)
        alignments = MemorySkillAlignmentIndex.objects.filter(memory__assistant_id=assistant_id)
        return Response({
            "training_maps": list(maps.values()),
            "memory_alignment": list(alignments.values()),
        })
