import { useEffect, useState } from "react";

export function useRecentVectorMemories() {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchVectorMemories() {
      try {
        const response = await fetch("/api/memory/vector/");
        if (!response.ok) throw new Error("Failed to load vector memories");
        const data = await response.json();
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