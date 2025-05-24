import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SimulationGridViewer() {
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/simulation/simulation-grid/")
      .then((res) => setClusters(res.results || res))
      .catch(() => setClusters([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="my-3">
      <h5>Simulation Grid</h5>
      {loading && <div>Loading grid...</div>}
      <ul className="list-group">
        {clusters.map((c) => (
          <li key={c.id} className="list-group-item">
            {c.cluster_name} – {c.phase}
          </li>
        ))}
        {!loading && clusters.length === 0 && (
          <li className="list-group-item text-muted">No clusters.</li>
        )}
      </ul>
    </div>
  );
}
