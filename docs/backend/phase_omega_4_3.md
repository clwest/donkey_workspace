# Phase Ω.4.3 — DocumentSet Memory Audit, Prompt Mutation Engine & Symbolic Retrieval Diff Viewer

Phase Ω.4.3 gives MythOS introspective memory awareness. Users can audit what was learned from a DocumentSet, mutate Codex prompts based on retrieval gaps, and visualize symbolic differences between sources. This completes the loop from ingestion to intelligent correction.

## Core Components
- **DocumentSetMemoryAudit** – analyze tokens learned from each source in a DocumentSet, summarizing Codex-linked tags and assistant memory clusters
- **PromptMutationEngine** – detect retrieval mismatches and mutate prompts across memory context with similarity scoring
- **SymbolicRetrievalDiffViewer** – compare embedding diffs between document chunks and prompt activations

### DocumentSetMemoryAudit Model
```python
class DocumentSetAuditReport(models.Model):
    document_set = models.ForeignKey(DocumentSet, on_delete=models.CASCADE)
    source_url = models.CharField(max_length=255)
    token_count = models.IntegerField()
    codex_tag_summary = models.JSONField()
    memory_cluster_stats = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Captures audit metrics from a DocumentSet including token counts and memory cluster stats.

### PromptMutationEngine Model
```python
class PromptMutationRecord(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    mutation_trace = models.JSONField()
    similarity_score = models.FloatField()
    saved_to_codex = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```
Stores mutated prompts with similarity scores and codex sync state.

### SymbolicRetrievalDiffViewer Model
```python
class RetrievalDiffTrace(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    memory_chunk = models.ForeignKey(SymbolicChunk, on_delete=models.CASCADE)
    activation_score = models.FloatField()
    suggested_rephrase = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Logs underperforming memory chunks and suggested rephrasing to improve resonance.

## View Routes
- `/document-set/:id/audit` – token counts by source, codex-tag summary and memory map
- `/prompts/:id/mutate` – analyze retrieval gaps and preview mutations
- `/memory/retrieval-diff/:assistantId` – list chunks with low activation and rephrase suggestions

## Testing Goals
- Verify audit reports aggregate token counts and codex tag summaries per source
- Ensure prompt mutations produce similarity scores and can be saved back to codex
- Confirm retrieval diff viewer highlights low-activation chunks and generates rephrasing tips

---
Prepares for Phase Ω.4.4 — Symbolic Summon Feedback Loops, Assistant Reflection Merges & MythOS Prompt Replay Lab
