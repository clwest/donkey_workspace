import apiFetch from "@/utils/apiClient";
import { clearCachedUser } from "@/hooks/useAuthGuard";
import { setToken, clearTokens, getRefreshToken } from "@/utils/auth";

export async function loginUser(email, password) {
  try {
    const data = await apiFetch("/token/", {
      method: "POST",
      body: { username: email, password },
    });
    setToken({ access: data.access, refresh: data.refresh });
    return data;
  } catch (err) {
    clearCachedUser();
    clearTokens();
    throw err;
  }
}

export async function registerUser(payload) {
  const data = await apiFetch("/dj-rest-auth/registration/", {
    method: "POST",
    body: payload,
  });
  if (data.access || data.refresh) {
    setToken({ access: data.access, refresh: data.refresh });
    return data;
  }
  return loginUser(payload.username || payload.email, payload.password1);
}

export function logoutUser() {
  clearTokens();
  clearCachedUser();
}

export async function refreshToken() {
  const refresh = getRefreshToken();
  if (!refresh) return null;
  const data = await apiFetch("/token/refresh/", {
    method: "POST",
    body: { refresh },
  });
  setToken({ access: data.access, refresh: data.refresh });
  return data;
}
