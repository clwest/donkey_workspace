from django.db import models

from .lore import ResurrectionTemplate, SwarmCodex

class SymbolicIdentityCard(models.Model):
    assistant = models.OneToOneField("assistant.Assistant", on_delete=models.CASCADE)
    archetype = models.CharField(max_length=100)
    symbolic_tags = models.JSONField()
    myth_path = models.CharField(max_length=100)
    purpose_signature = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"IdentityCard for {self.assistant.name}"


class PersonaTemplate(models.Model):
    template_name = models.CharField(max_length=100)
    default_role = models.CharField(max_length=100)
    tone_profile = models.TextField()
    resurrection_template = models.ForeignKey(
        ResurrectionTemplate, null=True, on_delete=models.SET_NULL
    )
    starter_codex = models.ForeignKey(
        SwarmCodex, null=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.template_name
