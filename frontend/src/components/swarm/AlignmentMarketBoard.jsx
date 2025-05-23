import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AlignmentMarketBoard() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    apiFetch("/agents/alignment-market/")
      .then((res) => setEntries(res.results || res))
      .catch(() => setEntries([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Alignment Market</h5>
      <ul className="list-group">
        {entries.map((e) => (
          <li key={e.id} className="list-group-item">
            {e.participant} – {e.access_level} ({e.alignment_score})
          </li>
        ))}
        {entries.length === 0 && (
          <li className="list-group-item text-muted">No market data.</li>
        )}
      </ul>
    </div>
  );
}
