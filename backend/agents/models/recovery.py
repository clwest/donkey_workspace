from django.db import models

from .lore import SwarmCodex


class RitualCompressionCache(models.Model):
    """Store compressed ritual payloads for rapid recovery."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    compressed_ritual_data = models.JSONField()
    symbolic_signature_hash = models.CharField(max_length=256)
    entropy_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"RitualCache {self.assistant_id}"


class AssistantDeploymentAutoRestarter(models.Model):
    """Auto-recover assistants from failure states."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    last_known_state = models.TextField()
    symbolic_fallback_path = models.TextField()
    restart_trigger_reason = models.CharField(max_length=100)
    successful_redeploy_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"AutoRestarter {self.assistant_id}"


class CodexProofOfSymbolEngine(models.Model):
    """Generate codex proof-of-symbol hashes for integrity checks."""

    codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    symbolic_checksum = models.CharField(max_length=256)
    directive_path_log = models.JSONField()
    mutation_trail_hash = models.TextField()
    proof_verification_status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"ProofEngine {self.codex_id}"
