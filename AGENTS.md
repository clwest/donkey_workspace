# 🤖 AGENTS.md — MythOS & Donkey Workspace

This file guides Codex (and other AI agents) to understand our project's architecture, conventions, and evolving capabilities.

---

## 🏗️ Project Overview

- **Project Name:** MythOS (aka Donkey Workspace)
- **Purpose:** A recursive symbolic AI system that ingests data, reflects, evolves, and self-documents across multi-agent structures — culminating in a central `/clarity` health dashboard.

---

## 🗂️ Project Structure

/agents.md ← This file
/README.md ← Main architecture & phase overview
/AGENTS.md ← (you are here)
/PHASE\_…md ← Phase plans (Ω.10, Ω.11, etc.)
/MYTHOS_YEAR_ONE_REVIEW.md ← Year‑One narrative & metrics
/PHASE_SUMMARY.md ← Master phase list
/docs/
/docs/core/ ← Active core docs
/docs/archive/ ← Archived/deprecated docs
/frontend/ ← UI/React components (e.g. ClarityPanel.jsx)
/backend/ ← API endpoints (e.g. clarity, diagnostics)

---

## 📘 Key Documentation Files

### Core Docs

- `README.md` — High-level architecture and roadmap
- `PHASE_...` — Phase-by-phase planning (latest: Ω.11.0 “Clarity Lock‑In”)
- `MYTHOS_YEAR_ONE_REVIEW.md` — Year‑One timeline and key milestones
- `Clarity_Panel_Spec.md` — UI/UX spec for `/clarity`

### Archives

- Old or exploratory `.md` files moved to `/docs/archive/` (for historical engineering embeds)

---

## 🛠️ Coding Conventions

- **Language/Stack:** Python (backend), Next.js & Tailwind CSS (frontend), PostgreSQL (PGVector)
- **Utilities Naming:** `run_xyz_diagnostics`, `validate_anchors`, `mutate_glossary_anchors`, etc.
- **Prompt & Mutation Logs:** Use `PromptMutationLog`, `TrustScore`, and `SymbolicAnchorReviewPage`

---

## ⚙️ Core Workflows (Agents)

1. **Document Ingestion → RAG → Glossary Recall**  
   Use `run_rag_diagnostics` to verify chunk retrieval, anchor hits, fallback rates.

2. **Memory → Reflection → Prompt Mutation**  
   On reflection: log prompt diff, trigger mutation chain, update symbolic anchors.

3. **Chat → Feedback → Anchor Mutation**  
   Chat UI supports thumbs up/down and tags—feedback is linked to anchor scoring and dynamic glossary updates.

4. **Clarity Health Panel**  
   `/clarity` route shows assistant snapshots, including memory/reflection counts, trust, drift, fallback rates, prompt lineage, and diagnostic controls.

---

## 📐 Design & Testing Guidelines

- Use Tailwind for UI styling—ensure ClarityPanel follows existing dashboard patterns
- Prompt diffs should render Git-style changes
- API endpoints:
  - `GET /api/assistants/clarity/` — list all assistant states
  - `GET /api/assistants/{slug}/clarity/` — single assistant detail
  - `POST /api/assistants/{slug}/refresh_clarity/` — trigger diagnostics refresh
- Write backend tests around new models (TrustScore, AnchorStats)
- Use Codex to generate MD and PDF output via export routes

---

## 📚 Documentation for AI Agents

Codex should ingest the following `.md` files to guide generation:

- `README.md`
- `PHASE_...` plans (especially Ω.11.0)
- `MYTHOS_YEAR_ONE_REVIEW.md`
- `Clarity_Panel_Spec.md`

Archived files are excluded to reduce noise.  
If new `.md` files are added under `/docs/core/`, update this AGENTS.md accordingly.

---

## 🧭 Codex Behavior Expectations

- Follow naming conventions and file structure
- Only modify code in relevant folders; never touch archived `.md`s
- Use diagnostic endpoints and health panel schema for UI logic
- Generate changes in small, reviewable PRs linked to phase goals
- Style frontend code with Tailwind and functional React components

---

## 🧪 Testing & CI Workflow

- Run `pytest` for backend and integrate anchor/diagnostic coverage
- Use `jest` or similar for frontend ClarityPanel tests
- Ensure code quality: linters, type checks, commit standards

---

## 📈 Why This Matters

A well-structured `AGENTS.md` boosts Codex productivity by **75% accuracy** and cuts review time dramatically—ideally aligning code outputs with project architecture and style guidelines 🔁 [oai_citation:0‡vibecoding.com](https://www.vibecoding.com/2025/06/05/how-to-configure-agents-md-files-to-supercharge-your-codex-ai-agent-performance/?utm_source=chatgpt.com) [oai_citation:1‡productcompass.pm](https://www.productcompass.pm/p/ai-agent-architectures?utm_source=chatgpt.com) [oai_citation:2‡agentsmd.net](https://agentsmd.net/?utm_source=chatgpt.com).

---

> Codex: **Use this as your map.** It’s your guide to what we’ve built, where we’re heading, and how to operate within MythOS.
