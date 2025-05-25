# 🧠 MythOS Route Map (Frontend ↔ Backend Alignment)

Compiled for Codex routing, view integration, and component planning

\-\-\-

## 🔮 Assistant Routes

| Frontend Path | Backend URL | View | Serializer | Notes |
| ------------- | ----------- | ---- | ---------- | ----- |
| `/assistants/:id/interface` | `/api/assistants/:id/` | `AssistantInterfacePage` | `AssistantDetailSerializer` | Loads codex anchors, ritual launchpads, belief forks |
| `/assistants/:id/fork` | `/api/assistants/:id/belief-forks/` | `BeliefForkViewer` | `BeliefForkSerializer` | Fork visualization per memory/ritual divergence |
| `/assistants/:id/thoughts` | `/api/assistants/:id/thought-log/` | `ThoughtLogPanel` | `AssistantThoughtLogSerializer` | Chain-of-thought, ritual state, prompt lineage |
| `/assistants/:id/deck` | `/api/assistants/:id/personality-deck/` | `PersonalityDeckBuilder` | `AssistantPersonalityDeckSerializer` | Card-based role editor |
| `/assistants/:id/traits` | `/api/assistants/:id/traits/` | `AssistantTraitCardViewer` | `AssistantTraitCardSerializer` | Trait card deck with codex bar |

\-\-\-

## 📜 Codex Routes

| Frontend Path | Backend URL | View | Serializer | Notes |
| ------------- | ----------- | ---- | ---------- | ----- |
| `/codex` | `/api/codex/` | `CodexInteractionLayer` | `SwarmCodexSerializer` | Main codex viewer/editor |
| `/codex/converge` | `/api/codex/converge/` | `CodexConvergencePage` | `CodexConvergenceCeremonySerializer` | Merge codices via ritual |
| `/codex/proof` | `/api/codex/proof-of-symbol/` | `CodexProofLogViewer` | `CodexProofOfSymbolSerializer` | Proof trace hash validation |
| `/codex/evolve` | `/api/codex/evolve/` | `PromptMutationExplorer` | `CodexPromptMutationSerializer` | Prompt + role mutation lineage |
| `/codex/orchestrator/:assistantId` | `/api/codex/orchestrator/` | `CodexPromptOrchestrator` | `PromptUsageLogSerializer` | Assistant prompt editor/previewer |
| `/codex/vote` | `/api/metrics/codex/vote/` | `CodexVotePage` | `CodexClauseVoteSerializer` | Clause mutation ballots |

\-\-\-

## 🔁 Ritual Routes

| Frontend Path | Backend URL | View | Serializer | Notes |
| ------------- | ----------- | ---- | ---------- | ----- |
| `/ritual` | `/api/ritual/launchpads/` | `RitualDashboardPage` | `RitualLaunchpadSerializer` | Main ritual launcher with codex links |
| `/ritual/composer` | `/api/ritual/compose/` | `RitualComposerPage` | `RitualDraftSerializer` | Ritual blueprint editor |
| `/ritual/containers` | `/api/ritual/containers/` | `RitualContainerPanel` | `RitualFunctionContainerSerializer` | Persistent execution state viewer |
| `/ritual/fork/replay` | `/api/ritual/fork-replay/` | `RitualForkReplayPage` | `RitualForkReplaySerializer` | Side-by-side ritual replays with divergence tagging |
| `/ritual/reputation` | `/api/metrics/ritual/reputation/` | `RitualReputationPage` | `RitualReputationScoreSerializer` | Ritual rating tracker |

\-\-\-

## ⏳ Memory + Dream + Replay

| Frontend Path | Backend URL | View | Serializer | Notes |
| ------------- | ----------- | ---- | ---------- | ----- |
| `/timeline` | `/api/memory/timeline/` | `MemoryTimelineViewer` | `MemoryTimelineSerializer` | Role-tagged memory braid |
| `/dream/rebirth` | `/api/dream/rebirth/` | `DreamRebirthPage` | `DreamframeRebirthSerializer` | Dream-based assistant reincarnation trigger |
| `/assistants/:id/dream/debug` | `/api/assistants/:id/dream/debug/` | `DreamTriggerDebugger` | `DreamTriggerLogSerializer` | Dreamframe state debugger |
| `/replay/engine` | `/api/replay/engine/` | `SymbolicReplayEnginePage` | `SymbolicReplayEngineSerializer` | Full scenario memory playback with codex echo |
| `/assistants/:id/fork/replay` | `/api/assistants/:id/fork-replay/` | `ForkDrivenMemoryPlayback` | `MemoryForkPlaybackSerializer` | Memory fork comparison |
| `/swarm/playback` | `/api/simulation/swarm-reflection-playback/` | `SwarmReflectionPlaybackPage` | `SwarmReflectionPlaybackLogSerializer` | Multi-assistant reflection timeline |
| `/swarm/alignment` | `/api/metrics/swarm/alignment/` | `SwarmAlignmentPage` | `SwarmAlignmentIndexSerializer` | Swarm belief stability index |
| `/swarm/rewire` | `/api/swarm/rewire/` | `SwarmAgentRewirePage` | `SwarmAgentRouteSerializer` | Swarm relationship map |
| `/cascade/:id` | `/api/simulation/prompt-cascades/:id/` | `PromptCascadeWatcherPage` | `PromptCascadeLogSerializer` | View prompt chain cascade |
| `/simulation/grid` | `/api/simulation/simulation-grid/` | `SimulationGridPage` | `SimulationClusterStatusSerializer` | Live simulation status grid |
| `/simulate/narrative` | `/api/simulate/narrative/` | `NarrativeMutationSimulatorPage` | `NarrativeMutationTraceSerializer` | Narrative rewrite sandbox |

\-\-\-

## 🌍 Federation + Council

| Frontend Path | Backend URL | View | Serializer | Notes |
| ------------- | ----------- | ---- | ---------- | ----- |
| `/guilds/council` | `/api/guilds/council/` | `GuildArbitrationCouncilPage` | `MythicArbitrationCouncilSerializer` | Multi-guild codex/treaty vote logic |
| `/treaty/forge` | `/api/treaty/forge/` | `TreatyEditorPage` | `SymbolicTreatyProtocolSerializer` | Treaty builder |
| `/federation/codices` | `/api/federation/codices/` | `CodexFederationPage` | `CodexFederationArchitectureSerializer` | Federated codex cluster viewer |

\-\-\-

## 🛠️ Deployment, Dev, Orchestration

| Frontend Path | Backend URL | View | Serializer | Notes |
| ------------- | ----------- | ---- | ---------- | ----- |
| `/deploy/standards` | `/api/deploy/standards/` | `DeploymentStandardsPage` | `BeliefAlignedDeploymentStandardSerializer` | Symbolic check for launch environments |
| `/summon/federated` | `/api/summon/federated/` | `FederatedSummonPage` | `FederatedMythicIntelligenceSummonerSerializer` | Multi-assistant swarm summoning logic |
| `/project/composer` | `/api/project/composer/` | `MythOSProjectComposerPage` | `AssistantProjectSerializer` | Task milestone planner |
| `/debug/prompts` | `/api/images/debug/prompts/` | `PromptDebuggerPage` | `PromptMutationLogSerializer` | Prompt diff + codex trace map |
| `/prompts/capsules` | `/api/prompts/capsules/` | `PromptCapsuleManagerPage` | `PromptCapsuleSerializer` | Shared prompt capsules |

\-\-\-

### 🔜 To Add (Phase X.5)
- `/audit/mythpath` → Assistant lifecycle narrative reviewer
- `/sandbox/ritual` → Codex clause + memory trigger playground

\-\-\-

_For every route: ensure the router passes the assistant `:id` parameter and sync component states with `symbolic_label`, `codex_id`, `ritual_id`, and `memory_signature` where required._
