import apiFetch from "../utils/apiClient";

export async function mutateMemory(id, style = "clarify") {
  const res = await apiFetch(`/memory/${id}/mutate/`, {
    method: "POST",
    body: { style },
  });
  return res;
}

export async function toggleBookmark(id, isBookmarked, label = "Important") {
  const endpoint = isBookmarked ? "unbookmark" : "bookmark";
  const res = await apiFetch(`/memory/${id}/${endpoint}/`, {
    method: "POST",
    body: isBookmarked ? null : { label },
  });
  return res;
}
