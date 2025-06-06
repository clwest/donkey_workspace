import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import apiFetch from "@/utils/apiClient";

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
    if (cachedUser) return;
    const token = localStorage.getItem("access");
    if (!token || tokenExpired(token)) {
      if (tokenExpired(token)) {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
      }
      setChecked(true);
      if (/^\/(assistants|onboarding|dashboard|memory|memories)/.test(location.pathname)) {
        navigate("/login", { replace: true });
      }
      return;
    }
    apiFetch("/auth/user/")
      .then((data) => {
        cachedUser = data;
        setUser(data);
        setError(null);
        setChecked(true);
      })
      .catch((err) => {
        console.error("auth check failed", err);
        setError(err);
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        setChecked(true);
        if (/^\/(assistants|onboarding|dashboard|memory|memories)/.test(location.pathname)) {
          navigate("/login", { replace: true });
        }
      });
  }, [navigate, location.pathname]);

  return { user, authChecked: checked, authError: error };
}
