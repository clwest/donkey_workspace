# Model Reference

This document lists notable models and their API exposure.

| Model | App | Active | Endpoint | Serializer |
|-------|-----|--------|----------|------------|
| AgentReactivationVote | agents | inactive | n/a | no |
| AssistantMythosLog | agents | inactive | n/a | no |
| AudioResponse | assistants | inactive | n/a | no |
| MemoryBranch | memory | inactive | n/a | no |
| MythLink | agents | inactive | n/a | no |
| NarrativeDebate | assistants | inactive | n/a | no |
| SwarmCadenceLog | agents | inactive | n/a | no |
| SwarmMemoryArchive | agents | inactive | n/a | no |
| LegacyArtifact | agents | active | /api/artifacts/ | LegacyArtifactSerializer |
| ReincarnationLog | agents | active | /api/reincarnations/ | ReincarnationLogSerializer |
| ReturnCycle | agents | active | /api/return-cycles/ | ReturnCycleSerializer |
| UserInteractionSummary | accounts | inactive | n/a | no |
| UserMemory | accounts | inactive | n/a | no |
| UserPrompts | accounts | inactive | n/a | no |

`verify_model_usage` management commands can be run per app to check if a model
has references elsewhere.
