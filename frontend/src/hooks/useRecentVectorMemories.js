import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export function useRecentVectorMemories() {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchVectorMemories() {
      try {
        const data = await apiFetch("/memory/vector/");
        setMemories(data);
      } catch (err) {
        console.error("Error fetching vector memories:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchVectorMemories();
  }, []);

  return { memories, loading };
}