import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function useTourActivation(slug) {
  const [status, setStatus] = useState(null);
  const [started, setStarted] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function activate() {
      if (!slug) return setLoading(false);
      try {
        const data = await apiFetch(`/assistants/${slug}/tour_started/`, {
          method: "POST",
          body: { source: "dashboard" },
        });
        setStatus(data.hint_status || null);
        setStarted(true);
      } catch (err) {
        console.error("tour activation", err);
      } finally {
        setLoading(false);
      }
    }
    activate();
  }, [slug]);

  return { isTourStarted: started, status, loading };
}
