import apiFetch from "../utils/apiClient";

export const fetchAgents = (params) => apiFetch("/agents/", { params });
export const fetchAgentThoughts = (slug) =>
  apiFetch(`/assistants/${slug}/thoughts/recent/`);
export const fetchRecentDelegations = () =>
  apiFetch("/assistants/delegation_events/recent/");

export const fetchArbitrationCases = () => apiFetch("/agents/arbitration-cases/");
export const fetchTreatyBreaches = () => apiFetch("/agents/treaty-breaches/");
export const fetchSymbolicSanctions = () => apiFetch("/agents/symbolic-sanctions/");
