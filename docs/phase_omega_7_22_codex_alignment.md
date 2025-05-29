# 🧠 Phase Ω.7.22 — Codex Directive Anchoring + Execution Focus

## 🧭 Purpose
Codex occasionally drifts or skips patch objectives when executing multi-part debugging or ingestion phases. This phase introduces **Codex directive anchoring** to ensure that Codex:

1. Fully reads and respects all task goals
2. Logs each objective as it is fulfilled
3. Stops only when all listed patch criteria are verified or flagged

---

## 🧠 Core Enhancements

### 🧩 1. Directive Parsing Layer
- Codex tasks will parse each phase into actionable sub-goals:
  - Detect checkboxes, bullet goals, and code injection points
- Store these as internal directives during execution

### 🧷 2. Execution Checklist Logging
- For each directive, Codex will:
  - Log `✅ Completed` or `❌ Skipped`
  - Show inline where each patch step was applied
  - Indicate whether fallback logic was triggered

### 🛑 3. Fail-Safe Guard
- Prevent Codex from submitting a patch if:
  - One or more required directives were not handled
  - Output is missing matching function/class if explicitly mentioned in the phase

---

## 🔧 Dev Implementation

### 🔹 Codex Prompt Injection
- [ ] Inject phase goals into Codex task header
- [ ] Wrap each task in a `@codex_directives` annotation block for parsing

### 🔹 Logging Helpers
- [ ] Add structured Codex log like:
```json
{
  "directive": "Suppress fallback junk chunks",
  "status": "completed",
  "applied_to": "rag_retriever.py line 84"
}
```

### 🔹 Dev Dashboard View (optional)
- [ ] Add `/codex/logs/` UI showing:
  - Directive name
  - Patch file + line
  - Status badge (✅/❌)

---

## 🧪 Verification

- [ ] Submit any multi-part phase (e.g. Ω.7.21.d) to Codex
- [ ] Confirm all checkboxes are logged as `completed`
- [ ] Codex returns full inline patch with status block
- [ ] If incomplete: Codex refuses patch and shows what’s missing

---

## 🔁 Related Phases

- Ω.7.21 — Chunk Glossary Match Scoring
- Ω.7.21.d — Fallback Chunk Override Patch
- Ω.6.4 — Ritual Drift Observation Engine

---

## 🧠 Why This Matters

Codex is the executor of your myth-building system. This phase ensures it:
- Honors all symbolic contracts
- Finishes what you start
- Helps **you** stay in the seat of strategic control