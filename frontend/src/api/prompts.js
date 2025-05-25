import apiFetch from "../utils/apiClient";

export async function fetchPrompts(query = "") {
  const q = query ? { search: query } : { show_all: "true" };
  return apiFetch(`/prompts/`, { params: q });
}

export async function fetchPromptBySlug(slug) {
  return apiFetch(`/prompts/${slug}/`);
}
