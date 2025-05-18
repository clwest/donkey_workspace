import { useState } from "react";
import apiFetch from "../utils/apiClient";

export function useGroupedReflection() {
  const [reflection, setReflection] = useState(() => {
    const cached = localStorage.getItem("grouped_devdoc_reflection");
    return cached ? JSON.parse(cached) : null;
  });

  const [loading, setLoading] = useState(false);

  const runSummarize = async () => {
    setLoading(true);
    try {
      const data = await apiFetch("/mcp/dev_docs/summarize/", {
        method: "POST",
      });

      if (data.summary) {
        setReflection(data);
        localStorage.setItem("grouped_devdoc_reflection", JSON.stringify(data));
      }
    } catch (err) {
      console.error("Failed to summarize docs:", err);
    } finally {
      setLoading(false);
    }
  };

  return { reflection, loading, runSummarize };
}
