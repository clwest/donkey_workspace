import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";
import { cachedUser } from "./useAuthGuard";
import { getAccessToken, getUserIdFromToken } from "@/utils/auth";

export default function useUserInfo() {
  const [user, setUser] = useState(() => {
    if (cachedUser) return cachedUser;
    const id = getUserIdFromToken();
    return id ? { id } : null;
  });

  useEffect(() => {
    if (cachedUser) {
      setUser(cachedUser);
      return;
    }
    const token = getAccessToken();
    if (!token) return;
    apiFetch("/user/", { allowUnauthenticated: true })
      .then((data) => {
        cachedUser = data;
        setUser(data);
      })
      .catch(() => {});
  }, []);

  return user;
}
