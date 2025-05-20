import apiFetch from "../utils/apiClient";

export function startCouncilSession(body) {
  return apiFetch("/council/start/", { method: "POST", body });
}

export function fetchCouncilSession(id) {
  return apiFetch(`/council/${id}/`);
}

export function fetchCouncilThoughts(id) {
  return apiFetch(`/council/${id}/thoughts/`);
}

export function respondToCouncil(id, body) {
  return apiFetch(`/council/${id}/respond/`, { method: "POST", body });
}

export function reflectCouncil(id) {
  return apiFetch(`/council/${id}/reflect/`, { method: "POST" });
}
