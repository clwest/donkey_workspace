import { useEffect, useState } from "react";

export default function DocumentUploadProgressBar({ progress }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    if (progress && progress.status === "completed") {
      const t = setTimeout(() => setVisible(false), 2000);
      return () => clearTimeout(t);
    }
    setVisible(true);
  }, [progress]);

  if (!progress || !visible) return null;

  const percent = (progress.processed / progress.total_chunks) * 100;
  let label = `📄 Processing ${progress.processed}/${progress.total_chunks}`;
  let icon = "📄";

  if (progress.status === "retrying") {
    icon = "🔄";
    label = "Attempting Codex-Aligned Rephrase";
  } else if (progress.status === "error") {
    icon = "⚠️";
    label = "Symbolic Drift Detected";
  } else if (progress.status === "completed") {
    icon = "✅";
    label = "Upload complete";
  }

  return (
    <div className="mt-3">
      <div className="progress">
        <div
          className="progress-bar"
          role="progressbar"
          style={{ width: `${percent}%` }}
          aria-valuenow={progress.processed}
          aria-valuemin="0"
          aria-valuemax={progress.total_chunks}
        ></div>
      </div>
      <small className="text-muted">
        {icon} {label}
      </small>
    </div>
  );
}
