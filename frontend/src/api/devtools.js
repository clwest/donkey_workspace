import apiFetch from "../utils/apiClient";

export function runCliCommand(body) {
  return apiFetch("/dev/cli/run/", { method: "POST", body });
}

export function fetchCommandLog(id) {
  return apiFetch(`/dev/command-logs/${id}/`);
}
