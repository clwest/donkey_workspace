import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function useUserInfo() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    apiFetch("/user/")
      .then(setUser)
      .catch(() => {});
  }, []);

  return user;
}
