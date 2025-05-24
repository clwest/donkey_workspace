import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualReputationBoard() {
  const [scores, setScores] = useState([]);

  useEffect(() => {
    apiFetch("/metrics/ritual/reputation/")
      .then((res) => setScores(res.results || res))
      .catch(() => setScores([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Ritual Reputation</h5>
      <ul className="list-group">
        {scores.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.ritual_name} – {s.rating}
          </li>
        ))}
        {scores.length === 0 && (
          <li className="list-group-item text-muted">No scores available.</li>
        )}
      </ul>
    </div>
  );
}
