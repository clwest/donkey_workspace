import React from "react";

export default function DocumentUploadProgressBar({ progress }) {
  if (!progress) return null;
  const percent = progress.percent_complete || 0;
  return (
    <div className="my-3">
      <div className="progress">
        <div
          className="progress-bar"
          role="progressbar"
          style={{ width: `${percent}%` }}
          aria-valuenow={percent}
          aria-valuemin="0"
          aria-valuemax="100"
        />
      </div>
      <small className="text-muted">
        {progress.stage} – {percent}%
      </small>
    </div>
  );
}
