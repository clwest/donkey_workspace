export default function ImportProgress({ progress }) {
  if (!progress) return null;
  const percent = (progress.processed / progress.total_chunks) * 100;
  return (
    <div className="mt-2">
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
        {progress.status === "completed" ? "✅" : ""} {progress.processed}/
        {progress.total_chunks}
      </small>
    </div>
  );
}
