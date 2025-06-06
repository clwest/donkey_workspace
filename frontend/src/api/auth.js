import apiFetch from "@/utils/apiClient";

export async function loginUser(email, password) {
  const data = await apiFetch("/token/", {
    method: "POST",
    body: { username: email, password },
  });
  if (data.access) localStorage.setItem("access", data.access);
  if (data.refresh) localStorage.setItem("refresh", data.refresh);
  return data;
}

export async function registerUser(payload) {
  await apiFetch("/dj-rest-auth/registration/", { method: "POST", body: payload });
  return loginUser(payload.username || payload.email, payload.password1);
}

export function logoutUser() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
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
