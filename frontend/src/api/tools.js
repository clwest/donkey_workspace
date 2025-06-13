import apiFetch from "../utils/apiClient";

export const fetchTools = () => apiFetch("/tools/");
export const fetchTool = (id) => apiFetch(`/tools/${id}/`);
export const executeTool = (id, body) =>
  apiFetch(`/tools/${id}/execute/`, { method: "POST", body });
export const fetchToolLogs = (id) => apiFetch(`/tools/${id}/logs/`);
