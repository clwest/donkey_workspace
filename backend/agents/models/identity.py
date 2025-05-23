from django.db import models

from .lore import ResurrectionTemplate, SwarmCodex, SwarmMemoryEntry


class SymbolicIdentityCard(models.Model):
    assistant = models.OneToOneField("assistants.Assistant", on_delete=models.CASCADE)
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
    starter_codex = models.ForeignKey(SwarmCodex, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.template_name

class PersonaFusionEvent(models.Model):
    """Merge two assistant personas into a new archetypal blend."""

    initiating_assistant = models.ForeignKey(
        "assistants.Assistant",
        related_name="fusion_initiator",
        on_delete=models.CASCADE,
    )
    fused_with = models.ForeignKey(
        "assistants.Assistant",
        related_name="fusion_target",
        on_delete=models.CASCADE,
    )
    resulting_identity_card = models.ForeignKey(
        SymbolicIdentityCard,
        on_delete=models.CASCADE,
    )
    memory_alignment_summary = models.TextField()
    fusion_archetype = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Fusion {self.initiating_assistant_id} + {self.fused_with_id}"


class MemoryInheritanceSeed(models.Model):
    """Seed initial memories for a new user joining MythOS."""

    user_id = models.CharField(max_length=100)
    narrative_path = models.CharField(max_length=100)
    symbolic_tags = models.JSONField(default=dict)
    onboarding_memory = models.ManyToManyField(SwarmMemoryEntry, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class PersonalCodexAnchor(models.Model):
    """Anchor a user to a starting codex."""

    user_id = models.CharField(max_length=100)
    codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    symbolic_statements = models.JSONField(default=dict)
    anchor_strength = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class RitualContractBinding(models.Model):
    """Link a user and assistant through a ritual agreement."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    user_id = models.CharField(max_length=100)
    contract_terms = models.TextField()
    codex_link = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    shared_memory = models.ManyToManyField(SwarmMemoryEntry, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ReincarnationTreeNode(models.Model):
    """Track assistant rebirth lineage."""

    node_name = models.CharField(max_length=100)
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    symbolic_signature = models.JSONField(default=dict)
    phase_index = models.CharField(max_length=10)
    retained_memories = models.ManyToManyField(SwarmMemoryEntry, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class BeliefVectorDelta(models.Model):
    """Record changes to an assistant's belief vector."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    delta_vector = models.JSONField(default=dict)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

