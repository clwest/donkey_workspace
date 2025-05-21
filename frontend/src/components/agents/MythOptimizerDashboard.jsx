import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythOptimizerDashboard() {
  const [report, setReport] = useState(null);

  useEffect(() => {
    apiFetch("/agents/myth-optimize/")
      .then(setReport)
      .catch((err) => console.error("Failed to optimize myth", err));
  }, []);

  if (!report) return <div>Loading myth architecture...</div>;

  return (
    <div className="card mb-3">
      <div className="card-header">Myth Architecture Report</div>
      <div className="card-body">
        <pre className="small">{JSON.stringify(report, null, 2)}</pre>
      </div>
    </div>
  );
}
