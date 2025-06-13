# Link DevDocs to Documents and ensure summaries + reflections exist

python manage.py repair_devdoc_links

# NEW — Auto-repair any unlinked or missing summaries and reflect

python manage.py relink_devdocs

# Cleanup unused or duplicate assistant slugs

python manage.py cleanup_orphan_assistants

# ─── PHASE 1: Embedding Repair + Sync ────────────────────────────

python manage.py fix_embedding_content
python manage.py repair_embedding_links
python manage.py repair_flagged_embeddings
python manage.py repair_all_embeddings
python manage.py audit_embedding_links --diff

# ─── PHASE 2: Context-Level Repair + Drift Snapshots ─────────────

python manage.py repair_context_embeddings --assistant claritybot
python manage.py log_embedding_drift

# ─── PHASE 3: Assistant Reflection + Document Sync ───────────────

python manage.py reflect_on_document --doc <document_id> --assistant claritybot
python manage.py audit_document_reflections
python manage.py summarize_reflection_group --group claritybot

# ─── PHASE 4: Glossary Anchor Inference + Mutation Suggestions ───

python manage.py infer_glossary_anchors --assistant claritybot
python manage.py generate_missing_mutations_for_assistant claritybot

# ─── PHASE 5: Retry Birth Reflections + Audit Status ─────────────

python manage.py retry_birth_reflection --all
python manage.py audit_birth_reflections --failed-only --json

# ─── PHASE 6: DevDoc Repair + Assistant Cleanup ──────────────────

python manage.py repair_devdoc_links
python manage.py cleanup_orphan_assistants
python manage.py relink_devdocs

# ─── PHASE 7: Full Sweep & Validation (Optional) ─────────────────

python manage.py repair_assistants_boot
python manage.py repair_all_embeddings

💡 Helpful Commands You Can Run Anytime

Command Purpose
audit_embedding_links --diff See per-record mismatches and orphaned embeddings

reflect_on_document Trigger assistant document reflection

log_embedding_drift Snapshot embedding mismatch drift across contexts

retry_birth_reflection Re-run assistant intro reflection if failed

generate_missing_mutations_for_assistant Suggest glossary term fixes

cleanup_orphan_assistants Identify unused or duplicate assistants

repair_context_embeddings Fix memory context-specific links (requires valid assistant)
