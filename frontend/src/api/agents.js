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

export const fetchInsightHubs = () => apiFetch("/insight-hubs/");
export const fetchPerspectiveMerges = () => apiFetch("/perspective-merges/");
export const fetchTimelineStitchLogs = () => apiFetch("/timeline-stitching/");
export const fetchRitualMastery = () => apiFetch("/agents/ritual-mastery/");
export const fetchPilgrimages = () => apiFetch("/agents/pilgrimages/");
export const initiateReincarnation = (assistant_id) =>
  apiFetch("/agents/reincarnation/", { method: "POST", body: { assistant_id } });

