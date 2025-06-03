export default function MoodStabilityGauge({ score = 1 }) {
  const pct = Math.round(score * 100);
  let color = "bg-success";
  if (score < 0.4) color = "bg-danger";
  else if (score < 0.7) color = "bg-warning";

  return (
    <div className="ms-2" title={`Health ${pct}%`} style={{ width: "60px" }}>
      <div className="progress" style={{ height: "6px" }}>
        <div className={`progress-bar ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

