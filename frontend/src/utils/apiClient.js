const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export default async function apiFetch(url, options = {}) {
  const { params, ...fetchOptions } = options;
  const defaultHeaders = fetchOptions.body
    ? { "Content-Type": "application/json" }
    : {};

  let fullUrl = API_URL + url;
  if (params) {
    const q = new URLSearchParams(params).toString();
    if (q) {
      fullUrl += (url.includes("?") ? "&" : "?") + q;
    }
  }

  const res = await fetch(fullUrl, {
    ...fetchOptions,
    headers: {
      ...defaultHeaders,
      ...(fetchOptions.headers || {}),
    },
    body:
      fetchOptions.body && typeof fetchOptions.body !== "string"
        ? JSON.stringify(fetchOptions.body)
        : fetchOptions.body,
    credentials: "include",
  });

  if (!res.ok) {
    console.error(`API Error ${res.status}: ${res.statusText}`);
    throw new Error("API Error");
  }

  return res.json();
}

// Media helpers
export const fetchImages = (params) =>
  apiFetch(`/images/`, { params });

export const generateImage = (payload) =>
  apiFetch(`/images/generate/`, { method: "POST", body: payload });

export const fetchCharacters = () => apiFetch(`/characters/profiles/`);

export const fetchStories = () => apiFetch(`/stories/`);
