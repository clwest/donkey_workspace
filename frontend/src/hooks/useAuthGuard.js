import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import { toast } from "react-toastify";
import { getToken, clearTokens } from "@/utils/auth";

export let cachedUser = null;
let authUserFailCount = 0;

function tokenExpired(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

export default function useAuthGuard({ allowUnauthenticated = false } = {}) {
  const [user, setUser] = useState(cachedUser);
  const [checked, setChecked] = useState(Boolean(cachedUser));
  const [error, setError] = useState(null);
  const [authErrorHandled, setAuthErrorHandled] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const authDebug =
    new URLSearchParams(location.search).get("debug") === "auth";

  useEffect(() => {
    async function checkAuth() {
      if (authErrorHandled) return;

      if (cachedUser) {
        setChecked(true);
        setUser(cachedUser);
        return;
      }

      const token = getToken();
      console.log("\ud83d\udd10 Auth Check \u2192 JWT found?", Boolean(token));
      if (!token) {
        setChecked(true);
        if (!allowUnauthenticated) {
          navigate("/login", { replace: true });
        }
        return;
      }
      if (tokenExpired(token)) {
        if (authDebug) console.warn("[auth] access token expired");
        clearTokens();
        if (!allowUnauthenticated && !["/login", "/register"].includes(location.pathname)) {
          toast.warning("Session expired. Please log in again.");
          setError(new Error("Unauthorized"));
          setAuthErrorHandled(true);
          if (/^\/(assistants|onboarding|dashboard|memory|memories)/.test(location.pathname)) {
            navigate("/login", { replace: true });
          }
        }
        setChecked(true);
        return;
      }

      try {
        const data = await apiFetch("/auth/user/", { allowUnauthenticated });
        cachedUser = data;
        authUserFailCount = 0;
        setUser(data);
        setError(null);
        setChecked(true);

        if (data.assistant_count === 0 && !location.pathname.startsWith("/onboarding")) {
          if (!location.pathname.startsWith("/assistants/launch")) {
            toast.info("Launch your first assistant to get started");
            navigate("/assistants/launch", { replace: true });
          }
          return;
        }
        if (!data.onboarding_complete) {
          if (!location.pathname.startsWith("/onboarding")) {
            toast.info("Finish onboarding to unlock your dashboard");
            navigate("/onboarding/world", { replace: true });
          }
          return;
        }
        if (location.pathname === "/" || location.pathname === "/home") {
          navigate("/assistants/primary/dashboard", { replace: true });
        }
      } catch (err) {
        console.warn("auth_user endpoint failed", err);
        authUserFailCount += 1;
        if (!allowUnauthenticated && authUserFailCount >= 2) {
          setError(err);
          clearTokens();
          if (!["/login", "/register"].includes(location.pathname)) {
            toast.warning("Session expired. Please log in again.");
          }
          setAuthErrorHandled(true);
          if (/^\/(assistants|onboarding|dashboard|memory|memories)/.test(location.pathname)) {
            navigate("/login", { replace: true });
          }
        } else if (!allowUnauthenticated) {
          setError(err);
        }
        setChecked(true);
      }
    }
    checkAuth();
  }, [navigate, authErrorHandled, allowUnauthenticated]);

  return { user, authChecked: checked, authError: error };
}

export function clearCachedUser() {
  cachedUser = null;
}
