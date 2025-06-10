import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function useAssistantIdentity(slug, { allowUnauthenticated = false } = {}) {
  const [identity, setIdentity] = useState(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (!slug) return;
    let active = true;
    apiFetch(`/assistants/${slug}/identity/`, { allowUnauthenticated })
      .then((d) => {
        if (active) {
          setIdentity(d);
          setLoaded(true);
        }
      })
      .catch((err) => {
        if (err.status === 403 && !allowUnauthenticated) {
          apiFetch(`/assistants/${slug}/identity/`, { allowUnauthenticated: true })
            .then((d) => {
              if (active) {
                setIdentity(d);
                setLoaded(true);
              }
            })
            .catch(() => {
              if (active) {
                setIdentity(null);
                setLoaded(true);
              }
            });
        } else if (err.status === 404 || err.status === 403) {
          console.warn("Demo identity or recap not available");
          if (active) {
            setIdentity(null);
            setLoaded(true);
          }
        } else {
          console.error("Failed to load identity", err);
          if (active) {
            setIdentity(null);
            setLoaded(true);
          }
        }
      });
    return () => {
      active = false;
    };
  }, [slug]);

  return { identity, loaded };
}
