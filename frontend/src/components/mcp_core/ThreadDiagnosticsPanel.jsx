import React from "react";

export default function ThreadDiagnosticsPanel({ thread }) {
  if (!thread || thread.continuity_score == null) return null;

  const score = thread.continuity_score;
  let emoji = "🟢";
  if (score < 0.4) emoji = "🔴";
  else if (score < 0.75) emoji = "🟡";

  return (
    <div className="d-flex align-items-center my-2">
      <span style={{ fontSize: "1.5rem" }} className="me-2">
        {emoji}
      </span>
      <div>
        <div className="fw-bold">Health Score: {Math.round(score * 100)}%</div>
        {thread.last_diagnostic_run && (
          <div className="text-muted small">
            Last checked {new Date(thread.last_diagnostic_run).toLocaleString()}
          </div>
        )}
      </div>
    </div>
  );
}
