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

export const fetchSymbolicReflections = ({ assistantId, campaignId } = {}) => {
  let url = "/memory/list/?symbolic_change=true";
  if (assistantId) url += `&assistant_id=${assistantId}`;
  if (campaignId) url += `&campaign_id=${campaignId}`;
  return apiFetch(url);
};
