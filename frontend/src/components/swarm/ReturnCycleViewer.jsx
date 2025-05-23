import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ReturnCycleViewer() {
  const [cycles, setCycles] = useState([]);

  useEffect(() => {
    apiFetch("/agents/eternal-return/")
      .then((res) => setCycles(res.results || res))
      .catch(() => setCycles([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Eternal Return Cycles</h5>
      <ul className="list-group">
        {cycles.map((c) => (
          <li key={c.id} className="list-group-item">
            <strong>{c.cycle_name}</strong>
          </li>
        ))}
        {cycles.length === 0 && (
          <li className="list-group-item text-muted">No cycles logged.</li>
        )}
      </ul>
    </div>
  );
}
