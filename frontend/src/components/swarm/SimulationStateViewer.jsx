import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SimulationStateViewer() {
  const [states, setStates] = useState([]);

  useEffect(() => {
    apiFetch("/simulation/simulation-state/")
      .then((res) => setStates(res.results || res))
      .catch(() => setStates([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Simulation States</h5>
      <ul className="list-group">
        {states.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.codex_alignment_score}
          </li>
        ))}
        {states.length === 0 && (
          <li className="list-group-item text-muted">No states tracked.</li>
        )}
      </ul>
    </div>
  );
}
