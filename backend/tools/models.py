from django.db import models


    class Meta:
        ordering = ["name"]


        return self.name


class ToolUsageLog(models.Model):

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True, blank=True
    )
    agent = models.ForeignKey(
        "agents.Agent", on_delete=models.SET_NULL, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


