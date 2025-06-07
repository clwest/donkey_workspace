// Determine the base API url.  If VITE_API_URL is not defined or looks malformed
// (e.g. only contains a port like ":8000/api"), fall back to using the current
// page origin.  This prevents "Failed to fetch" errors when the env variable is
// missing a hostname.
import {
  getAccessToken,
  clearTokens,
  getRefreshToken,
  saveAuthTokens,
} from "./auth";
import { toast } from "react-toastify";

let API_URL = import.meta.env.VITE_API_URL;

// Track auth state and redirect behavior to avoid infinite loops
let authLost = false;
let lastRedirect = 0;
let redirectCount = 0;
let sessionExpiredNotified = false;
let isRedirecting = false;

export function resetAuthState() {
  authLost = false;
  isRedirecting = false;
  sessionExpiredNotified = false;
}
const authDebug =
  new URLSearchParams(window.location.search).get("debug") === "auth";

export async function tryRefreshToken() {
  const refresh = getRefreshToken();
  if (!refresh) return false;
  if (authDebug) console.log("[auth] attempting token refresh");
  try {
    const res = await fetch(`${API_URL}/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
      credentials: "include",
    });
    if (!res.ok) return false;
    const data = await res.json();
    saveAuthTokens({ access: data.access, refresh: data.refresh });
    resetAuthState();
    if (authDebug) console.log("[auth] refresh succeeded");
    return true;
  } catch (err) {
    if (authDebug) console.warn("[auth] refresh failed", err);
    return false;
  }
}

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
  if (authLost && !options.allowUnauthenticated) {
    throw new Error("Unauthorized");
  }

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

  const doFetch = async () => {
    const token = getAccessToken();
    if (!token && authDebug) console.warn("[auth] access token missing");
    return fetch(fullUrl, {
      ...fetchOptions,
      headers: {
        ...defaultHeaders,
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(fetchOptions.headers || {}),
      },
      body:
        fetchOptions.body && typeof fetchOptions.body !== "string"
          ? JSON.stringify(fetchOptions.body)
          : fetchOptions.body,
      credentials: "include",
    });
  };

  let res = await doFetch();

  if (res.status === 401) {
    if (authDebug) console.warn(`[auth] 401 from ${url}`);
    if (!url.startsWith("/auth/user")) {
      const refreshed = await tryRefreshToken();
      if (refreshed) {
        res = await doFetch();
      }
    }
  }

  if (res.status === 401) {
    if (!sessionExpiredNotified && !options.allowUnauthenticated) {
      toast.warning("Session expired. Please log in again.");
      sessionExpiredNotified = true;
    }
    if (!authLost && !options.allowUnauthenticated && !isRedirecting) {
      authLost = true;
      isRedirecting = true;
      clearTokens();
      const now = Date.now();
      if (now - lastRedirect < 2000) {
        redirectCount += 1;
        if (redirectCount > 2) {
          console.warn("More than 2 redirects occur within 2s");
        }
      } else {
        redirectCount = 1;
      }
      lastRedirect = now;
      if (window.location.pathname === "/login") {
        window.location.assign("/login");
      } else {
        const next = encodeURIComponent(window.location.pathname);
        window.location.assign(`/login?next=${next}`);
      }
    }
    throw new Error("Unauthorized");
  }

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

  if (res.status === 204 || res.status === 205) {
    // No content to parse
    return null;
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
