# Phase Ω.6.3 — Reflection-Based Prompt Migration, Codex Rescoring Loops & Mythpath Optimizer

Phase Ω.6.3 turns reflection into a first-class infrastructure feature. Prompts can migrate between assistants, codex clauses are rescored by swarm feedback, and mythpaths adapt to performance trends.

## Core Components
- **PromptMigrationLog** – records each migration and links to the originating prompt.
- **PromptPerformanceContext** – tracks reflection scores and retry recovery data.
- **CodexClauseScoreLog** – stores score changes for codex clauses.
- **SwarmClauseResonance** – aggregates swarm behavior affecting clause scores.
- **MythpathPerformanceTrace** – captures mythpath outcomes and narrative alignment.
- **ArchetypeMutationProposal** – suggested updates for an assistant's mythpath.

## View Routes
- `/prompts/migrate` – migrate prompts between assistants or projects.
- `/codex/score` – codex rescoring dashboard with delta graphs.
- `/mythpath/optimizer` – propose archetype or system prompt refinements.

## Testing Goals
- Prompt migrations persist to `PromptMigrationLog` with lineage tracking.
- Codex rescoring loops update `CodexClauseScoreLog` and show deltas over time.
- Mythpath optimizer outputs `ArchetypeMutationProposal` records for review.

---
Prepares for Phase Ω.6.4 — Swarm Agent Rewiring, Prompt Capsule Propagation & Codified Narrative Mutation Simulator
