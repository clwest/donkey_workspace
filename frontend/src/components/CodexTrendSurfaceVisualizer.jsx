import { useEffect, useState } from "react";
import { getCodexTrends } from "../api/agents";

export default function CodexTrendSurfaceVisualizer() {
  const [cycles, setCycles] = useState([]);

  useEffect(() => {
    getCodexTrends()
      .then((res) => setCycles(res.results || res))
      .catch(() => setCycles([]));
  }, []);

  return (
    <div className="p-2 border rounded">
      <h5>Codex Trend Surface</h5>
      <ul className="list-group">
        {cycles.map((c) => (
          <li key={c.id} className="list-group-item">
            {c.cycle_name || c.id}
          </li>
        ))}
        {cycles.length === 0 && (
          <li className="list-group-item text-muted">No trend data.</li>
        )}
      </ul>
    </div>
  );
}
