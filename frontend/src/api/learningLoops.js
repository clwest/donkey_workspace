import apiFetch from "../utils/apiClient";

export async function triggerAdaptiveLoop(assistantId) {
  const res = await apiFetch(`/learning-loops/trigger/${assistantId}/`, {
    method: "POST",
  });
  return res;
}
