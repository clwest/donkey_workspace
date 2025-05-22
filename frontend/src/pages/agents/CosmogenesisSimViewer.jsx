import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function CosmogenesisSimViewer() {
  const [sims, setSims] = useState([]);

  useEffect(() => {
    apiFetch("/agents/cosmogenesis/")
      .then(setSims)
      .catch(() => setSims([]));
  }, []);

  return (
    <div className="container my-5">
      <h1>Cosmogenesis Simulations</h1>
      <ul className="list-group mt-3">
        {sims.map((s) => (
          <li key={s.id} className="list-group-item">
            <strong>{s.title}</strong> - {s.resulting_cosmos_map?.slice(0, 50)}
          </li>
        ))}
        {sims.length === 0 && (
          <li className="list-group-item text-muted">No simulations</li>
        )}
      </ul>
    </div>
  );
}
