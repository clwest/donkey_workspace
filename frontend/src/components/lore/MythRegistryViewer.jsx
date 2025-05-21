import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythRegistryViewer() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    apiFetch("/agents/myth-registry/")
      .then(setEntries)
      .catch(() => setEntries([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Myth Registry</h5>
      <ul className="list-group">
        {entries.map((e) => (
          <li key={e.id} className="list-group-item">
            <strong>{e.memory}</strong> - {e.signature}
          </li>
        ))}
        {entries.length === 0 && (
          <li className="list-group-item text-muted">No entries found.</li>
        )}
      </ul>
    </div>
  );
}
