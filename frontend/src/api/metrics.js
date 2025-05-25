import apiFetch from "../utils/apiClient";

export async function fetchPerformanceMetrics(assistantId) {
  return apiFetch(`/metrics/performance/${assistantId}/`);
}
