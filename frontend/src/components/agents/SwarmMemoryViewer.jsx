import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SwarmMemoryViewer() {
  const [entries, setEntries] = useState([]);
  const [tag, setTag] = useState("");

  useEffect(() => {
    let url = "/agents/swarm-memory/";
    if (tag) url += `?tag=${tag}`;
    apiFetch(url)
      .then(setEntries)
      .catch(() => setEntries([]));
  }, [tag]);

  return (
    <div className="my-3">
      <h5>Swarm Memory</h5>
      <div className="mb-2">
        <input
          type="text"
          className="form-control"
          placeholder="Filter by tag"
          value={tag}
          onChange={(e) => setTag(e.target.value)}
        />
      </div>
      <ul className="list-unstyled">
        {entries.map((m) => (
          <li key={m.id} className="mb-2">
            <strong>{m.title}</strong> - {m.origin}
          </li>
        ))}
        {entries.length === 0 && (
          <li className="text-muted">No swarm memory found.</li>
        )}
      </ul>
    </div>
  );
}
