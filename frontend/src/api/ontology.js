import apiFetch from "../utils/apiClient";

export const fetchCascadeGraph = (clauseId) =>
  apiFetch(`/cascade/${clauseId}/`);

export const fetchRoleCollisions = () => apiFetch(`/collisions/`);

export const fetchCodexClauses = () => apiFetch(`/codex/clauses/`);

export const startStabilizationCampaign = (clauseId) =>
  apiFetch(`/stabilize/`, { method: "POST", body: { clause_id: clauseId } });

export const fetchStabilizationCampaigns = () =>
  apiFetch(`/stabilize/campaigns/`);

export const finalizeStabilizationCampaign = (id) =>
  apiFetch(`/stabilize/${id}/finalize/`, { method: "POST" });
