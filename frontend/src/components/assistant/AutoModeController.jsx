
import { useEffect, useState } from "react";
import apiFetch  from "../../utils/apiClient";


export default function useAutoReflectionLoop(projectId, enabled = false, intervalMs = 15000) {
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    if (!enabled || !projectId) return;

    let cancelled = false;

    const loop = async () => {
      if (cancelled) return;

      try {
        console.log("🧠 Generating Thought...");
        await apiFetch(`/assistants/projects/${projectId}/thoughts/generate/`, { method: "POST" });

        if (cancelled) return;
        console.log("💭 Reflecting on Thoughts...");
        const reflection = await apiFetch(`/assistants/projects/${projectId}/thoughts/reflect/`, { method: "POST" });

        console.log("📘 Reflection result:", reflection.reflection);
        // TODO: Add summary display, DB log, or planner trigger here
      } catch (err) {
        console.error("Auto-mode loop failed:", err);
      }
    };

    const interval = setInterval(loop, intervalMs);
    setIsRunning(true);

    return () => {
      cancelled = true;
      clearInterval(interval);
      setIsRunning(false);
    };
  }, [enabled, projectId, intervalMs]);

  return { isRunning };
}