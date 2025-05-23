import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function PatternClusterExplorer() {
  const [clusters, setClusters] = useState([]);
  useEffect(() => {
    apiFetch("/myth-patterns/").then(setClusters);
  }, []);

  return (
    <div className="p-2 border rounded">
      <h5>Myth Pattern Clusters</h5>
      <ul>
        {clusters.map((c) => (
          <li key={c.id}>{c.cluster_id} - {c.convergence_score}</li>
        ))}
      </ul>
    </div>
  );
}
