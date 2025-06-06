import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function useTourProgress(slug) {
  const [progress, setProgress] = useState(null);

  const load = async () => {
    if (!slug) return;
    try {
      const data = await apiFetch(`/assistants/${slug}/tour_progress/`);
      setProgress(data);
      return data;
    } catch (err) {
      console.error("tour progress", err);
    }
  };

  useEffect(() => {
    load();
  }, [slug]);

  return {
    ...progress,
    refresh: load,
  };
}
