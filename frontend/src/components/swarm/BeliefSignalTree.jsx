import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function BeliefSignalTree() {
  const [signals, setSignals] = useState([]);

  useEffect(() => {
    apiFetch("/agents/belief-signals/")
      .then((res) => setSignals(res.results || res))
      .catch(() => setSignals([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Belief Signals</h5>
      <ul className="list-group">
        {signals.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.origin_assistant} → {s.receivers?.join?.(", ") || ""}
          </li>
        ))}
        {signals.length === 0 && (
          <li className="list-group-item text-muted">No signals recorded.</li>
        )}
      </ul>
    </div>
  );
}
