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
export const fetchTimelineReflections = () => apiFetch("/timeline-reflection/");
export const createTimelineReflection = (body) =>
  apiFetch("/timeline-reflection/", { method: "POST", body });
export const fetchArchetypeFusionEvents = () => apiFetch("/archetype-fusion/");
export const createArchetypeFusionEvent = (body) =>
  apiFetch("/archetype-fusion/", { method: "POST", body });

export const fetchResonanceGraphs = () => apiFetch("/agents/resonance-graphs/");
export const fetchCognitiveBalance = () => apiFetch("/agents/cognitive-balance/");
export const fetchPurposeMigrations = () =>
  apiFetch("/agents/purpose-migrations/");

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
