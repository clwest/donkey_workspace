# 🧠 MANAGEMENT_COMMANDS.md

_A curated reference for running assistant system maintenance, diagnostics, and repair tasks._

---

## 🔄 PHASE 0: DevDoc Linking + Seeding

```bash
python manage.py repair_devdoc_links
python manage.py relink_devdocs
python manage.py cleanup_orphan_assistants
```

---

## 🔧 PHASE 1: Embedding Repair + Sync

```bash
python manage.py fix_embedding_content
python manage.py repair_embedding_links
python manage.py repair_flagged_embeddings
python manage.py repair_all_embeddings
python manage.py audit_embedding_links --diff
python manage.py repair_low_score_embeddings --threshold 0.2
python manage.py repair_embedding_metadata --summary
```

---

## 🧬 PHASE 2: Context Repair + Drift Tracking

```bash
python manage.py repair_context_embeddings --assistant <slug|uuid>
python manage.py log_embedding_drift
```

---

## 🪞 PHASE 3: Assistant Reflection + Document Sync

```bash
python manage.py reflect_on_document --doc <uuid> --assistant <slug|uuid>
python manage.py audit_document_reflections
python manage.py summarize_reflection_group --group <uuid>
python manage.py retry_doc_reflections
```

---

## 🧠 PHASE 4: Glossary Anchor Inference + Mutation

```bash
python manage.py infer_glossary_anchors --assistant <slug|uuid>
python manage.py generate_missing_mutations_for_assistant <slug>
python manage.py validate_anchors
python manage.py score_symbolic_anchors
```

---

## 🎯 PHASE 5: Birth Reflection Recovery

```bash
python manage.py retry_birth_reflection --all
python manage.py audit_birth_reflections --failed-only --json
```

---

## 🧰 PHASE 6: RAG Diagnostics + Anchor Drift

```bash
python manage.py run_rag_tests --assistant <slug|uuid>
python manage.py sync_missing_diagnostics
python manage.py inspect_rag_failure --doc <uuid>
python manage.py generate_diagnostic_reports
python manage.py export_embedding_audit_report
python manage.py track_anchor_drift
```

---

## 📊 PHASE 7: Growth + Trust Signals

```bash
python manage.py refresh_trust_profile
python manage.py patch_growth_state
python manage.py sync_missing_links
```

---

## 🧩 PHASE 8: Topic Grouping + Anchor Tagging

```bash
python manage.py group_documents_by_topic
```

---

## ✅ PHASE 9: Assistant Boot + Final Sweep

```bash
python manage.py repair_assistants_boot
python manage.py repair_all_embeddings
```

---

## 🔁 Phase X: Upload Recovery & Chunk Recheck

```bash
python manage.py repair_failed_documents
python manage.py repair_document_chunk_flags
```
