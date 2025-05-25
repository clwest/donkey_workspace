# Phase Ω.6.2 — Swarm Task Evolution Engine, Memory-Optimized Skill Planner & Auto-Prompter Feedback Refinement

Phase Ω.6.2 elevates MythOS from simple task execution to adaptive learning. Patterns from recent task runs are mined for improvements, skill training maps overlay memory gaps, and prompt feedback is automatically linked to future mutations.

## Core Components
- **TaskEvolutionSuggestion** – suggestion derived from clusters of task runs.
- **PromptVersionTrace** – links prompt versions with feedback scores.
- **SwarmTaskCluster** – groups similar task runs for pattern mining.
- **SkillTrainingMap** – maps assistant skills to memory references.
- **MemorySkillAlignmentIndex** – tracks how well memory supports a skill.
- **TrainingSuggestionFeedbackLog** – logs feedback on training suggestions.
- **PromptFeedbackVector** – stores feedback scores for a prompt.
- **PromptMutationEffectTrace** – traces effect of a mutation using feedback.

## View Routes
- `/evolve/swarm` – swarm task evolution dashboard.
- `/plan/skills/:assistantId` – memory‑optimized skill planner.
- `/feedback/prompts/:promptId` – auto‑prompter feedback refinement panel.

## Testing Goals
- Suggestions can be created from task runs and retrieved via `/evolve/swarm`.
- Skill plans return training maps and alignment indexes for an assistant.
- Prompt feedback traces show version history linked with feedback scores.

---
Prepares for Phase Ω.6.3 — Reflection-Based Prompt Migration, Codex Rescoring Loops & Mythpath Optimizer
