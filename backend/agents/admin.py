from django.contrib import admin

# Register your models here.
from .models import (
    Agent,
    AgentThought,
    LoreEntry,
    RetconRequest,
    RealityConsensusVote,
)

admin.site.register(Agent)
admin.site.register(AgentThought)
admin.site.register(LoreEntry)
admin.site.register(RetconRequest)
admin.site.register(RealityConsensusVote)
