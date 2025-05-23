import { useMemo } from "react";

export function useCodexAlert(state) {
  return useMemo(() => {
    if (!state) return null;
    const { entropy_level = 0, coherence_index = 1, alignment_drift = 0 } = state;
    if (entropy_level > 0.7 || alignment_drift > 0.6) return "danger";
    if (coherence_index < 0.4) return "warning";
    return "stable";
  }, [state]);
}
