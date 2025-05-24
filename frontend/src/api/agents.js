import apiFetch from "../utils/apiClient";

export const fetchAgents = (params) => apiFetch("/agents/", { params });
export const fetchAgentThoughts = (slug) =>
  apiFetch(`/assistants/${slug}/thoughts/recent/`);
export const fetchRecentDelegations = () =>
  apiFetch("/assistants/delegation_events/recent/");

export const fetchArbitrationCases = () => apiFetch("/agents/arbitration-cases/");
export const fetchTreatyBreaches = () => apiFetch("/agents/treaty-breaches/");
export const fetchSymbolicSanctions = () => apiFetch("/agents/symbolic-sanctions/");
export const fetchTribunalCases = () => apiFetch("/agents/tribunals/");
export const fetchRestorativeMemoryActions = () => apiFetch("/agents/restorative-memory/");
export const fetchReputationRebirths = () => apiFetch("/agents/reputation-rebirths/");
export const fetchCosmologicalRoles = () => apiFetch("/agents/cosmological-roles/");
export const createMythWeave = (assistant, depth = 3) =>
  apiFetch("/agents/myth-weaver/", { method: "POST", body: { assistant, depth } });
export const fetchLegacyVaults = () => apiFetch("/agents/legacy-vaults/");
export const fetchCollaborationThreads = () =>
  apiFetch("/agents/collaboration-threads/");
export const fetchDelegationStreams = () =>
  apiFetch("/agents/delegation-streams/");
export const fetchMythflowInsights = () =>
  apiFetch("/agents/mythflow-insights/");

export const fetchKnowledgeReplications = () =>
  apiFetch("/agents/knowledge-replication/");
export const fetchMemoryBroadcasts = () =>
  apiFetch("/agents/memory-broadcasts/");
export const fetchLearningReservoirs = () =>
  apiFetch("/agents/learning-reservoirs/");

export const fetchMythflowPlans = () =>
  apiFetch("/agents/mythflow-plans/");
export const fetchDirectiveMemory = () =>
  apiFetch("/agents/directive-memory/");
export const fetchPlanningLattices = () =>
  apiFetch("/agents/planning-lattices/");


export const fetchCosmologies = () => apiFetch("/cosmologies/");
export const updateBeliefEngine = (id) =>
  apiFetch(`/belief-engine/${id}/update/`, { method: "POST" });
export const fetchPurposeArchives = () => apiFetch("/purpose-archives/");


export const fetchIdentityCards = () => apiFetch("/identity-cards/");
export const createIdentityCard = (body) =>
  apiFetch("/identity-cards/", { method: "POST", body });
export const fetchPersonaTemplates = () => apiFetch("/persona-templates/");
export const createPersonaTemplate = (body) =>
  apiFetch("/persona-templates/", { method: "POST", body });
export const onboardAssistant = (body) =>
  apiFetch("/onboarding/", { method: "POST", body });
export const fetchTimelineReflections = () => apiFetch("/timeline-reflection/");
export const createTimelineReflection = (body) =>
  apiFetch("/timeline-reflection/", { method: "POST", body });
export const fetchArchetypeFusionEvents = () => apiFetch("/archetype-fusion/");
export const createArchetypeFusionEvent = (body) =>
  apiFetch("/archetype-fusion/", { method: "POST", body });

export const fetchPersonaFusions = () => apiFetch("/persona-fusions/");
export const createPersonaFusion = (body) =>
  apiFetch("/persona-fusions/", { method: "POST", body });

export const fetchDialogueMutations = () => apiFetch("/dialogue-mutations/");
export const createDialogueMutation = (body) =>
  apiFetch("/dialogue-mutations/", { method: "POST", body });

export const fetchSceneDirectorFrames = () => apiFetch("/scene-director/");
export const createSceneDirectorFrame = (body) =>
  apiFetch("/scene-director/", { method: "POST", body });

export const fetchResonanceGraphs = () => apiFetch("/agents/resonance-graphs/");
export const fetchCognitiveBalance = () => apiFetch("/agents/cognitive-balance/");
export const fetchPurposeMigrations = () =>
  apiFetch("/agents/purpose-migrations/");
export const fetchLegacyRings = () => apiFetch("/agents/legacy-rings/");
export const fetchMemoryDendro = () => apiFetch("/agents/memory-dendro/");
export const fetchLifespanModels = () => apiFetch("/agents/lifespan-models/");

export const fetchStoryfields = () => apiFetch("/agents/storyfields/");
export const fetchMythPatterns = () => apiFetch("/agents/myth-patterns/");
export const fetchIntentHarmony = () => apiFetch("/agents/intent-harmony/");
export const fetchTrainingGrounds = () => apiFetch("/training-grounds/");
export const createTrainingGround = (body) =>
  apiFetch("/training-grounds/", { method: "POST", body });
export const fetchMythEditLogs = () => apiFetch("/myth-edit-log/");
export const createMythEditLog = (body) =>
  apiFetch("/myth-edit-log/", { method: "POST", body });
export const fetchLegacyContinuityVaults = () =>
  apiFetch("/legacy-continuity-vaults/");
export const createLegacyContinuityVault = (body) =>
  apiFetch("/legacy-continuity-vaults/", { method: "POST", body });

export const fetchVisualArchetypeCard = (assistantId) =>
  apiFetch(`/mythos/assistants/${assistantId}/archetype-card/`);

export const fetchAvailableRituals = (params) =>
  apiFetch(`/mythos/ritual-launchpads/`, { params });

export const fetchCodexInteraction = () => apiFetch(`/mythos/codex/`);

export const fetchCodexAnchors = (assistantId) =>
  apiFetch(`/assistants/${assistantId}/codex-anchors/`);

export const fetchMythRecordingSessions = () => apiFetch("/myth/record/");
export const createMythRecordingSession = (body) =>
  apiFetch("/myth/record/", { method: "POST", body });

export const fetchSymbolicDocs = () => apiFetch("/docs/symbolic/");
export const createSymbolicDoc = (body) =>
  apiFetch("/docs/symbolic/", { method: "POST", body });

export const fetchBeliefArtifacts = () => apiFetch("/artifacts/archive/");
export const createBeliefArtifact = (body) =>
  apiFetch("/artifacts/archive/", { method: "POST", body });

export const fetchDirectiveTracker = (id) =>
  apiFetch(`/assistants/${id}/directive-tracker/`);
export const fetchIdentityCard = (id) =>
  apiFetch(`/assistants/${id}/identity-card/`);
export const updateIdentityCard = (id, body) =>
  apiFetch(`/assistants/${id}/identity-card/`, { method: "PUT", body });
export const triggerRitualAction = (id, action) =>
  apiFetch(`/assistants/${id}/ritual/${action}/`, { method: "POST" });

export const getCodexTrends = () => apiFetch("/agents/codex/trends/");
export const fetchSymbolicForecasts = () => apiFetch("/agents/forecast/symbolic/");
export const fetchAssistantSentiments = (assistantId) =>
  apiFetch(`/agents/assistants/${assistantId}/sentiment/`);
export const fetchRitualMarketFeeds = () => apiFetch("/agents/market/rituals/");
export const fetchTrendReactivityModels = () =>
  apiFetch("/agents/assistants/trend-reactivity/");
export const fetchStabilityGraphs = () => apiFetch("/agents/system/stability/");
export const fetchAssistantThoughtLog = (id) => apiFetch(`/assistants/${id}/thought-log/`);

export const fetchTrainedAgents = () => apiFetch("/agents/trained/");
export const promoteTrainedAgent = (logId) =>
  apiFetch("/assistants/promote/", { method: "POST", body: { log_id: logId } });
