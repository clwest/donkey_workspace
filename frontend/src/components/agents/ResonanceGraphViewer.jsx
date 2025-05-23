import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ResonanceGraphViewer() {
  const [graphs, setGraphs] = useState([]);

  useEffect(() => {
    apiFetch("/agents/resonance-graphs/")
      .then(setGraphs)
      .catch(() => setGraphs([]));
  }, []);

  if (graphs.length === 0) {
    return <div>No resonance graphs.</div>;
  }

  return (
    <div className="card">
      <div className="card-header">Symbolic Resonance Graphs</div>
      <ul className="list-group list-group-flush">
        {graphs.map((g) => (
          <li key={g.id} className="list-group-item">
            <strong>{g.scope}</strong> – {new Date(g.generated_at).toLocaleString()}
            <pre className="mt-2 mb-0" style={{ whiteSpace: "pre-wrap" }}>
              {JSON.stringify(g.resonance_map, null, 2)}
            </pre>
          </li>
        ))}
      </ul>
    </div>
  );
}
