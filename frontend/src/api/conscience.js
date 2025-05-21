import apiFetch from "../utils/apiClient";

export const listConscienceProfiles = () => apiFetch("/conscience/");
export const createConscienceProfile = (payload) =>
  apiFetch("/conscience/", { method: "POST", body: payload });

export const runBeliefAudit = (assistantSlug) =>
  apiFetch("/reflexive-epistemology/", {
    method: "POST",
    body: { assistant: assistantSlug },
  });

export const createDecisionFramework = (payload) =>
  apiFetch("/decision-frameworks/", { method: "POST", body: payload });
