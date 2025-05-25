import apiFetch from "../utils/apiClient";

export async function fetchMythgraph(id) {
  return apiFetch(`/simulation/mythgraph/assistant/${id}/`);
}
