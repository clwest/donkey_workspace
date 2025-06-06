import { useState, useEffect } from "react";
import { getToken } from "@/utils/auth";

export default function useAuth() {
  const [token, setToken] = useState(getToken());

  useEffect(() => {
    const handler = () => setToken(getToken());
    window.addEventListener("storage", handler);
    return () => window.removeEventListener("storage", handler);
  }, []);

  return token;
}
