import apiFetch from "@/utils/apiClient";
import { clearCachedUser } from "@/hooks/useAuthGuard";

export async function loginUser(email, password) {
  try {
    const data = await apiFetch("/token/", {
      method: "POST",
      body: { username: email, password },
    });
    if (data.access) localStorage.setItem("access", data.access);
    if (data.refresh) localStorage.setItem("refresh", data.refresh);
    return data;
  } catch (err) {
    clearCachedUser();
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    throw err;
  }
}

export async function registerUser(payload) {
  await apiFetch("/dj-rest-auth/registration/", { method: "POST", body: payload });
  return loginUser(payload.username || payload.email, payload.password1);
}

export function logoutUser() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  clearCachedUser();
}

export async function refreshToken() {
  const refresh = localStorage.getItem("refresh");
  if (!refresh) return null;
  const data = await apiFetch("/token/refresh/", {
    method: "POST",
    body: { refresh },
  });
  if (data.access) localStorage.setItem("access", data.access);
  return data;
}
