import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function useAssistantIdentity(slug, { allowUnauthenticated = false } = {}) {
  const [identity, setIdentity] = useState(null);

  useEffect(() => {
    if (!slug) return;
    let active = true;
    apiFetch(`/assistants/${slug}/identity/`, { allowUnauthenticated })
      .then((d) => {
        if (active) setIdentity(d);
      })
      .catch((err) => {
        if (err.status === 404 || err.status === 403) {
          console.warn("Demo identity or recap not available");
          if (active) setIdentity(null);
        } else {
          console.error("Failed to load identity", err);
          if (active) setIdentity(null);
        }
      });
    return () => {
      active = false;
    };
  }, [slug]);

  return identity;
}
