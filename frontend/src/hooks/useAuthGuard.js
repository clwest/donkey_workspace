import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import { toast } from "react-toastify";
import { getToken, clearTokens } from "@/utils/auth";

export let cachedUser = null;

function tokenExpired(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

export default function useAuthGuard() {
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
      if (!token || tokenExpired(token)) {
        if (authDebug) console.warn("[auth] access token missing or expired");
        clearTokens();
        toast.warning("Not logged in");
        setChecked(true);
        setError(new Error("Unauthorized"));
        setAuthErrorHandled(true);
        if (/^\/(assistants|onboarding|dashboard|memory|memories)/.test(location.pathname)) {
          navigate("/login", { replace: true });
        }
        return;
      }

      try {
        const data = await apiFetch("/auth/user/");
        cachedUser = data;
        setUser(data);
        setError(null);
        setChecked(true);

        if (data.assistant_count === 0) {
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
        setError(err);
        clearTokens();
        toast.warning("Not logged in");
        setChecked(true);
        setAuthErrorHandled(true);
        if (/^\/(assistants|onboarding|dashboard|memory|memories)/.test(location.pathname)) {
          navigate("/login", { replace: true });
        }
      }
    }
    checkAuth();
  }, [navigate, location.pathname, authErrorHandled]);

  return { user, authChecked: checked, authError: error };
}

export function clearCachedUser() {
  cachedUser = null;
}
