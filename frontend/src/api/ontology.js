import apiFetch from "../utils/apiClient";

export const fetchCascadeGraph = (clauseId) =>
  apiFetch(`/cascade/${clauseId}/`);

export const fetchRoleCollisions = () => apiFetch(`/collisions/`);

export const startStabilizationCampaign = (clauseId) =>
  apiFetch(`/stabilize/`, { method: "POST", body: { clause_id: clauseId } });
