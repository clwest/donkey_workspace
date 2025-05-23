from django.db import models


class SymbolicUXPlaybook(models.Model):
    """Codifies UI patterns tied to an assistant archetype and codex tone."""

    playbook_name = models.CharField(max_length=150)
    archetype = models.CharField(max_length=100)
    tone_profile = models.TextField()
    ui_patterns = models.JSONField()
    codex_linked_rules = models.ManyToManyField('agents.SwarmCodex')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.playbook_name


class RoleDrivenUITemplate(models.Model):
    """Defines assistant view layout per symbolic function."""

    template_name = models.CharField(max_length=150)
    assigned_role = models.CharField(max_length=100)
    layout_config = models.JSONField()
    aura_overlay = models.TextField()
    active_traits = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.template_name


class SymbolicToolkitRegistry(models.Model):
    """Persistent symbolic toolsets tied to a user."""

    user_id = models.CharField(max_length=150)
    ritual_macros = models.JSONField(default=dict, blank=True)
    codex_shortcuts = models.JSONField(default=dict, blank=True)
    assistant_triggers = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Toolkit for {self.user_id}"
