import { useState, useEffect, useCallback } from "react";
import apiFetch from "@/utils/apiClient";
import {
  getToken,
  clearTokens,
} from "@/utils/auth";
import { loginUser, registerUser, logoutUser as apiLogout } from "@/api/auth";

export default function useAuth() {
  const [token, setTokenState] = useState(getToken());
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const tk = getToken();
    console.log(
      "\ud83d\udd10 Auth Check \u2192 JWT found?",
      Boolean(tk)
    );
    if (!tk) {
      setTokenState(null);
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const info = await apiFetch("/auth/user/", { allowUnauthenticated: true });
      setTokenState(tk);
      setUser(info);
    } catch {
      clearTokens();
      setTokenState(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
    const handler = () => setTokenState(getToken());
    window.addEventListener("storage", handler);
    return () => window.removeEventListener("storage", handler);
  }, [loadUser]);

  const login = useCallback(
    async (email, password) => {
      await loginUser(email, password);
      await loadUser();
    },
    [loadUser]
  );

  const register = useCallback(
    async (payload) => {
      await registerUser(payload);
      await loadUser();
    },
    [loadUser]
  );

  const logout = useCallback(() => {
    apiLogout();
    setTokenState(null);
    setUser(null);
  }, []);

  const isAuthenticated = Boolean(token && user);

  return { token, user, loading, isAuthenticated, login, register, logout };
}
