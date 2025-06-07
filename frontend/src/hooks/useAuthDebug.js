import { useState, useEffect } from "react";
import { getAccessToken, getRefreshToken } from "@/utils/auth";
import { getAuthLost } from "@/utils/apiClient";

export default function useAuthDebug() {
  const [access, setAccess] = useState(getAccessToken());
  const [refresh, setRefresh] = useState(getRefreshToken());
  const [authLost, setAuthLost] = useState(getAuthLost());

  useEffect(() => {
    function updateTokens() {
      setAccess(getAccessToken());
      setRefresh(getRefreshToken());
    }
    window.addEventListener("storage", updateTokens);
    return () => window.removeEventListener("storage", updateTokens);
  }, []);

  useEffect(() => {
    const id = setInterval(() => {
      setAuthLost(getAuthLost());
    }, 1000);
    return () => clearInterval(id);
  }, []);

  return { access, refresh, authLost };
}
