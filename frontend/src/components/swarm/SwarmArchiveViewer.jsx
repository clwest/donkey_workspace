import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SwarmArchiveViewer() {
  const [archives, setArchives] = useState([]);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch(`/swarm/archives/`, {
          params: filter ? { search: filter } : {},
        });
        setArchives(res.results || res);
      } catch (err) {
        console.error("Failed to load archives", err);
      }
    }
    load();
  }, [filter]);

  return (
    <div>
      <div className="d-flex mb-2">
        <input
          type="text"
          className="form-control me-2"
          placeholder="Search archives..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
      </div>
      <ul className="list-group">
        {archives.map((a) => (
          <li key={a.id} className="list-group-item">
            <strong>{a.title}</strong>
            {a.sealed && <span className="badge bg-secondary ms-2">Sealed</span>}
            <p className="mb-1 small">{a.summary}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
