import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function useTourProgress(slug) {
  const [progress, setProgress] = useState(null);
  const [paused, setPaused] = useState(false);

  const load = async () => {
    if (!slug) return;
    try {
      const data = await apiFetch(`/assistants/${slug}/tour_progress/`);
      setProgress(data);
      setPaused(false);
      return data;
    } catch (err) {
      console.error("tour progress", err);
      if (err.status === 429) {
        setPaused(true);
      }
    }
  };

  useEffect(() => {
    setProgress(null);
    setPaused(false);
    load();
  }, [slug]);

  return {
    ...progress,
    refresh: load,
    paused,
  };
}
