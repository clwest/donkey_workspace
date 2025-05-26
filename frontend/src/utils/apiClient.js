// Determine the base API url.  If VITE_API_URL is not defined or looks malformed
// (e.g. only contains a port like ":8000/api"), fall back to using the current
// page origin.  This prevents "Failed to fetch" errors when the env variable is
// missing a hostname.
let API_URL = import.meta.env.VITE_API_URL;

function isMissingHost(url) {
  if (!url) return true;
  try {
    const parsed = new URL(url, window.location.origin);
    return !parsed.hostname;
  } catch {
    return true;
  }
}

if (isMissingHost(API_URL)) {
  const base = window.location.origin.replace(/\/$/, "");
  API_URL = `${base}/api`;
}

export default async function apiFetch(url, options = {}) {
  const { params, ...fetchOptions } = options;
  const defaultHeaders = fetchOptions.body
    ? { "Content-Type": "application/json" }
    : {};

  const authToken = localStorage.getItem("access");

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
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      ...(fetchOptions.headers || {}),
    },
    body:
      fetchOptions.body && typeof fetchOptions.body !== "string"
        ? JSON.stringify(fetchOptions.body)
        : fetchOptions.body,
    credentials: "include",
  });

  if (!res.ok) {
    let errorMsg = `API Error ${res.status}`;
    try {
      const errData = await res.json();
      const detail = errData.error || JSON.stringify(errData);
      errorMsg += `: ${detail}`;
    } catch {
      errorMsg += `: ${res.statusText}`;
    }
    console.error(errorMsg);
    throw new Error(errorMsg);
  }

  return res.json();
}

// Media helpers
// Fetch publicly visible images for gallery views
export const fetchImages = (params) =>
  apiFetch(`/images/gallery/`, { params });

export const generateImage = (payload) =>
  apiFetch(`/images/generate/`, { method: "POST", body: payload });

export const fetchCharacters = () => apiFetch(`/characters/profiles/`);

export const fetchStories = () => apiFetch(`/stories/`);

export { API_URL };
