export default function MoodStabilityGauge({ msi = 1 }) {
  const pct = Math.round(msi * 100);
  let color = "bg-success";
  if (msi < 0.5) color = "bg-danger";
  else if (msi < 0.8) color = "bg-warning";

  return (
    <div className="ms-2" title={`Stability ${pct}%`} style={{ width: "60px" }}>
      <div className="progress" style={{ height: "6px" }}>
        <div className={`progress-bar ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

