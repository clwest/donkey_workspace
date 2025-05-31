# Phase Ω.6.4 — Swarm Agent Rewiring, Prompt Capsule Propagation & Codified Narrative Mutation Simulator

Phase Ω.6.4 transforms assistant learning from individual evolution into swarm-scale knowledge transmission. Prompt capsules can now be shared across assistants and adjusted contextually. Swarm agent routing maps allow symbolic rewiring of assistant relationships. Narrative mutations are simulated and codified through a symbolic replay environment.

## 🔄 Swarm Agent Rewiring

**View Route**
- `/swarm/rewire`

**Features**
- Visual map of agent relationships
- Rewire tools: swap mentor, reroute relays, update shared prompt paths
- Show tag deltas and tone realignment paths

**Backend**
- `SwarmAgentRoute`
- `AgentSymbolicMap`

## 🧬 Prompt Capsule Propagation

**View Route**
- `/prompts/capsules`

**Features**
- Capsule preview: content, context, feedback score, tags
- Assign capsule to multiple assistants
- Modify tone & tags before injection
- Track propagation lineage

**Backend**
- `PromptCapsule`
- `CapsuleTransferLog`

## 🎭 Narrative Mutation Simulator

**View Route**
- `/simulate/narrative`

**Features**
- Load assistant memory, prompts, codex trace
- Apply mutations (prompt, memory, tone)
- Visualize divergence: new thought logs, clause shifts, identity drift
- Save simulation to `NarrativeMutationTrace`

**Backend**
- `NarrativeMutationTrace`
- `MutationOutcomeLog`
- `AssistantNarrativeFork`

## ✅ Dev Tasks
- Scaffold `/swarm/rewire`, `/prompts/capsules`, `/simulate/narrative`
- Add mutation diff + tone alignment view
- Connect capsules to assistant prompt mutation workflow

---
Prepares for Phase Ω.6.5 — Assistant Lifecycle Curator, Memory-Driven Codex Convergence Engine & MythOS Swarm Cognition Ledger
