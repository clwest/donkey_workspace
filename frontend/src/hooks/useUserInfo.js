import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";
import { cachedUser } from "./useAuthGuard";
import { getAccessToken } from "@/utils/auth";

export default function useUserInfo() {
  const [user, setUser] = useState(cachedUser);

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
