import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function NarrativeMutationSimulator() {
  const [traces, setTraces] = useState([]);

  useEffect(() => {
    apiFetch("/simulate/narrative/")
      .then((res) => setTraces(res.results || res))
      .catch(() => setTraces([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Narrative Mutation Simulator</h5>
      <ul className="list-group">
        {traces.map((t) => (
          <li key={t.id} className="list-group-item">
            Trace for {t.assistant_name || t.assistant}
          </li>
        ))}
        {traces.length === 0 && (
          <li className="list-group-item text-muted">No simulation data.</li>
        )}
      </ul>
    </div>
  );
}
