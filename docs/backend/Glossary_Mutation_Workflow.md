# 🧬 Glossary Mutation Workflow

## Overview

This document outlines the architecture, purpose, and mechanics of the glossary mutation system implemented in Phase Ω.9.38. This system enables assistants to identify failing glossary anchors and automatically propose or apply better alternatives — forming a self-correcting loop that improves RAG performance over time.

---

## 🧠 Why Glossary Mutation Matters

Many glossary terms fail to ground during assistant retrieval, triggering fallbacks or producing vague results. These failures can be caused by:

- Ambiguous anchor phrasing
- Context mismatch between term and memory
- Redundancy or oversaturation

Glossary mutation resolves this by:

- Identifying terms with frequent fallback events
- Extracting semantic context from assistant reflections
- Using Codex to generate alternative anchor phrases
- Optionally applying or staging replacements

---

## 🛠️ Key Components

### ✅ RAG Diagnostics

- Command: `run_rag_diagnostics`
- Generates fallback logs per glossary anchor
- Output: `claritybot_results.json` (or per-assistant)

### ✅ Mutation Trigger

- CLI: `mutate_glossary_anchors.py`
- Parses diagnostics JSON
- Looks for:
  - Anchors with `fallback_triggered=True`
  - `avg_score < 0.2` (low-quality matches)
- Supports flags:
  - `--assistant`
  - `--from-json`
  - `--apply`
  - `--save-to-review`

### ✅ Codex Mutation Engine

- Uses assistant memory and RAGGroundingLog context to generate replacement terms
- Output per failed anchor:

```yaml
Original: "alignment"
Suggestions:
- Goal coordination
- Strategic consistency
- Intent coherence

✅ SymbolicMemoryAnchor Mutation Tracking
	•	Adds mutation_source field to track where mutations come from:
	•	"rag_auto_suggest"
	•	"reflection_mutation"
	•	"manual_patch"

⸻

🔄 Mutation Cycle
	1.	Run Diagnostics
    python manage.py run_rag_diagnostics --assistant=claritybot --output=claritybot_results.json

	2.	Run Mutation Suggestions
    python manage.py mutate_glossary_anchors --assistant=claritybot --from-json=claritybot_results.json --save-to-review

	3.	(Optional) Apply Mutations Automatically
    python manage.py mutate_glossary_anchors --assistant=claritybot --from-json=claritybot_results.json --apply

    4.	Re-run Diagnostics
        •	Compare fallback count between runs
        •	Track glossary convergence

📊 Related Tools
	•	rank_glossary_anchors.py: CLI to score anchor health
	•	log_rag_debug(): Logs used chunks, fallback causes
	•	get_glossary_terms_from_reflections(): Extracts anchor phrases from assistant memory

⸻

🚀 Future Enhancements
	•	Add review UI for glossary suggestions
	•	Score glossary convergence over time
	•	Allow assistants to accept/reject their own mutations
	•	Integrate auto-mutation triggers into Codex reflection loop

⸻
```
