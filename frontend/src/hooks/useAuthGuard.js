import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import { toast } from "react-toastify";
import { getToken, clearTokens } from "@/utils/auth";
import { refreshToken } from "@/api/auth";

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
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    async function checkAuth() {
      if (cachedUser) {
        setChecked(true);
        setUser(cachedUser);
        return;
      }
      const token = getToken();
      if (!token || tokenExpired(token)) {
        if (tokenExpired(token)) {
          clearTokens();
        }
        setChecked(true);
        if (/^\/(assistants|onboarding|dashboard|memory|memories)/.test(location.pathname)) {
          navigate("/login", { replace: true });
        }
        return;
      }
      try {
        const data = await apiFetch("/user/");
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
        console.error("auth check failed", err);
        try {
          await refreshToken();
          const data = await apiFetch("/user/");
          cachedUser = data;
          setUser(data);
          setError(null);
          setChecked(true);
          return;
        } catch {
          setError(err);
          clearTokens();
          setChecked(true);
          if (/^\/(assistants|onboarding|dashboard|memory|memories)/.test(location.pathname)) {
            navigate("/login", { replace: true });
          }
        }
      }
    }
    checkAuth();
  }, [navigate, location.pathname]);

  return { user, authChecked: checked, authError: error };
}

export function clearCachedUser() {
  cachedUser = null;
}
