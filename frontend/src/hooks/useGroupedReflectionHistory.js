import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export function useGroupedReflectionHistory() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/mcp/dev_docs/grouped_history/")
      .then(setHistory)
      .catch((err) => {
        console.error("❌ Failed to load reflection history:", err);
        setHistory([]);
      })
      .finally(() => setLoading(false));
  }, []);

  return { history, loading };
}
