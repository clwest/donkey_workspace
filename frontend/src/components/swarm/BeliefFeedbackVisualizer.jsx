import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function BeliefFeedbackVisualizer() {
  const [signals, setSignals] = useState([]);

  useEffect(() => {
    apiFetch("/belief-feedback/")
      .then((res) => setSignals(res.results || res))
      .catch(() => setSignals([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Belief Feedback Signals</h5>
      <ul className="list-group">
        {signals.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.origin_type} → {s.target_codex}
          </li>
        ))}
        {signals.length === 0 && (
          <li className="list-group-item text-muted">No signals yet.</li>
        )}
      </ul>
    </div>
  );
}
