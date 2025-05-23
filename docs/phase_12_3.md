
# Phase 12.3 — Memory-Driven Belief Inheritance Trees

This phase introduces a new layer of symbolic history tracking. Assistants now record how beliefs evolve across memory interactions and ritual executions.

## Key Models

- **BeliefInheritanceTree** – maps assistant and user memories into a lineage style record.
- **RitualResponseArchive** – stores completed ritual logs with summaries and belief shifts.

## Export Utility

`create_myth_journey_package` bundles a user's journey into JSON and Markdown files. The package can include belief trees, ritual archives and referenced memories.

View routes:

- `/belief/tree` – list or create belief inheritance trees.
- `/ritual/archive` – list or create ritual response archives.



