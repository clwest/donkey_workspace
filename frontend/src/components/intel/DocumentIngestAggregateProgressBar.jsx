import React from "react";

export default function DocumentIngestAggregateProgressBar({ jobs }) {
  if (!jobs || jobs.length === 0) return null;
  const overall = Math.round(
    jobs.reduce((sum, j) => sum + (j.percent_complete || 0), 0) / jobs.length
  );
  return (
    <div className="my-3">
      <div className="progress">
        <div
          className="progress-bar"
          role="progressbar"
          style={{ width: `${overall}%` }}
          aria-valuenow={overall}
          aria-valuemin="0"
          aria-valuemax="100"
        />
      </div>
      <small className="text-muted">Symbolic Integration {overall}%</small>
    </div>
  );
}
