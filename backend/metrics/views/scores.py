from rest_framework import generics
from ..models import RitualReputationScore, CodexClauseVote, SwarmAlignmentIndex
from ..serializers import (
    RitualReputationScoreSerializer,
    CodexClauseVoteSerializer,
    SwarmAlignmentIndexSerializer,
)


class RitualReputationScoreListView(generics.ListCreateAPIView):
    queryset = RitualReputationScore.objects.all().order_by("-created_at")
    serializer_class = RitualReputationScoreSerializer


class CodexClauseVoteListView(generics.ListCreateAPIView):
    queryset = CodexClauseVote.objects.all().order_by("-created_at")
    serializer_class = CodexClauseVoteSerializer


class SwarmAlignmentIndexView(generics.ListCreateAPIView):
    queryset = SwarmAlignmentIndex.objects.all().order_by("-created_at")
    serializer_class = SwarmAlignmentIndexSerializer
