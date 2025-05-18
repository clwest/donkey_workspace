from django.contrib import admin

# Register your models here.
from .models import Agent, AgentThought

admin.site.register(Agent)
admin.site.register(AgentThought)