export default function TaskStatusBadge({ status, label }) {
  if (!status) return null;
  const map = {
    running: { cls: "bg-info", icon: "⏳" },
    queued: { cls: "bg-warning text-dark", icon: "⏳" },
    complete: { cls: "bg-success", icon: "✔" },
    error: { cls: "bg-danger", icon: "⚠️" },
    paused: { cls: "bg-warning text-dark", icon: "⏸️" },
  };
  const info = map[status] || { cls: "bg-secondary", icon: "" };
  return (
    <span className={`badge ${info.cls} ms-2`}>
      {info.icon} {label || status}
    </span>
  );
}
