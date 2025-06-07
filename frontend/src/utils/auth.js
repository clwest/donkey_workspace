import { resetAuthState } from "./apiClient.js";

export function getUserIdFromToken() {
  const token = localStorage.getItem("access");
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.user_id || payload.userId || payload.id || null;
  } catch (err) {
    console.error("Failed to decode auth token", err);
    return null;
  }
}

export function getAccessToken() {
  return localStorage.getItem("access") || null;
}

export function getToken() {
  return getAccessToken();
}

export function getRefreshToken() {
  return localStorage.getItem("refresh") || null;
}

export function saveAuthTokens({ access, refresh }) {
  if (access) localStorage.setItem("access", access);
  if (refresh) localStorage.setItem("refresh", refresh);
  resetAuthState();
}

export function setToken(tokens) {
  saveAuthTokens(tokens);
}

export function clearTokens() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
}
