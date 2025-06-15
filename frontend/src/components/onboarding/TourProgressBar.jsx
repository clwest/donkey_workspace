import { useState, useEffect } from "react";
import useTourProgress from "@/hooks/useTourProgress";
import useAssistantHints from "@/hooks/useAssistantHints";

export default function TourProgressBar({ assistantSlug }) {
  const progress = useTourProgress(assistantSlug);
  const { hints } = useAssistantHints(assistantSlug);
  const [autoRetry, setAutoRetry] = useState(false);

  useEffect(() => {
    if (autoRetry && progress.paused) {
      const id = setTimeout(() => progress.refresh(), 10000);
      return () => clearTimeout(id);
    }
  }, [autoRetry, progress]);

  if (!progress || typeof progress.percent_complete !== "number") return null;

  const next = hints.find((h) => h.id === progress.next_hint);
  const label = next ? next.label : progress.next_hint;

  return (
    <div className="d-flex align-items-center gap-2 mb-2" data-testid="tour-progress">
      <div className="progress flex-grow-1" style={{ height: "6px" }}>
        <div className="progress-bar" style={{ width: `${progress.percent_complete}%` }} />
      </div>
      {label && progress.percent_complete < 100 && (
        <small className="text-muted">Next: {label}</small>
      )}
      {progress.paused && (
        <span className="text-warning ms-2 d-flex align-items-center">
          Paused
          <div className="form-check form-switch ms-2">
            <input
              className="form-check-input"
              type="checkbox"
              id="tourAuto"
              checked={autoRetry}
              onChange={(e) => setAutoRetry(e.target.checked)}
            />
          </div>
        </span>
      )}
    </div>
  );
}
