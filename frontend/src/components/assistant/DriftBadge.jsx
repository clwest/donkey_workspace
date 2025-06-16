export default function DriftBadge({ score }) {
  let color = "secondary";
  if (score > 0.6) color = "danger";
  else if (score > 0.3) color = "warning";
  else color = "success";
  const pct = Math.round((score || 0) * 100);
  return <span className={`badge bg-${color}`}>{pct}%</span>;
}
