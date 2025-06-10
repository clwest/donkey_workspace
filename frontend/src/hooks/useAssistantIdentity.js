import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function useAssistantIdentity(
  slug,
  { allowUnauthenticated = false } = {},
) {
  const [identity, setIdentity] = useState(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (!slug) return;
    let active = true;

    async function load() {
      try {
        const data = await apiFetch(`/assistants/${slug}/identity/`, {
          allowUnauthenticated,
        });
        if (active) {
          setIdentity({
            ...data,
            name: data.display_name || data.persona_name || data.name,
          });
          setLoaded(true);
        }
      } catch (err) {
        try {
          const a = await apiFetch(`/assistants/${slug}/`, {
            allowUnauthenticated: true,
          });
          if (active) {
            setIdentity({ name: a.name });
            setLoaded(true);
          }
        } catch (err2) {
          if (active) {
            console.error("Failed to load identity", err2);
            setIdentity({ name: slug });
            setLoaded(true);
          }
        }
      }
    }

    load();
    return () => {
      active = false;
    };
  }, [slug]);

  return { identity, loaded };
}
