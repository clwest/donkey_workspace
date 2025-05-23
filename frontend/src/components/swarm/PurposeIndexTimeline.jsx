import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function PurposeIndexTimeline() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    apiFetch("/agents/purpose-index/")
      .then((res) => setEntries(res.results || res))
      .catch(() => setEntries([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Purpose Index</h5>
      <ul className="list-group">
        {entries.map((e) => (
          <li key={e.id} className="list-group-item">
            {e.assistant} – {e.timeline_marker}
          </li>
        ))}
        {entries.length === 0 && (
          <li className="list-group-item text-muted">No entries logged.</li>
        )}
      </ul>
    </div>
  );
}
