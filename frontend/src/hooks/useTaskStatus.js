import { useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function useTaskStatus(url) {
  const [isRunning, setIsRunning] = useState(false);
  const [hasRun, setHasRun] = useState(false);
  const [isError, setIsError] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  async function poll(taskId) {
    let status = "running";
    while (status === "running" || status === "queued") {
      await new Promise((r) => setTimeout(r, 1000));
      try {
        const res = await apiFetch(`/mcp/tasks/${taskId}/status/`);
        status = res.status?.toLowerCase();
      } catch {
        status = "error";
      }
    }
  }

  const trigger = async (options = {}) => {
    setIsRunning(true);
    setIsError(false);
    setIsPaused(false);
    try {
      const res = await apiFetch(url, { method: "POST", ...options });
      if (res?.task_id && res.status && res.status !== "complete") {
        await poll(res.task_id);
      }
      setIsRunning(false);
      setHasRun(true);
      setLastUpdated(Date.now());
      return res;
    } catch (err) {
      setIsRunning(false);
      setHasRun(true);
      setIsError(true);
      if (err.status === 429) setIsPaused(true);
      throw err;
    }
  };

  return { trigger, isRunning, hasRun, isError, isPaused, lastUpdated };
}
