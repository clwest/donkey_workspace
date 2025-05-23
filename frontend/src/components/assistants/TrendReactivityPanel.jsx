import { useEffect, useState } from "react";
import { fetchTrendReactivityModels } from "../../api/agents";

export default function TrendReactivityPanel() {
  const [models, setModels] = useState([]);

  useEffect(() => {
    fetchTrendReactivityModels()
      .then((res) => setModels(res.results || res))
      .catch(() => setModels([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Trend Reactivity Models</h5>
      <ul className="list-group">
        {models.map((m) => (
          <li key={m.id} className="list-group-item">
            Stability {m.symbolic_resonance_stability}
          </li>
        ))}
        {models.length === 0 && (
          <li className="list-group-item text-muted">No trend data.</li>
        )}
      </ul>
    </div>
  );
}
