from django.contrib import admin

# Register your models here.
from .models import Agent, AgentThought, SwarmJournalEntry

admin.site.register(Agent)
admin.site.register(AgentThought)
admin.site.register(SwarmJournalEntry)
