import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SwarmTimelineViewer() {
  const [date, setDate] = useState("");
  const [snapshot, setSnapshot] = useState(null);

  async function fetchSnapshot() {
    if (!date) return;
    try {
      const data = await apiFetch(`/swarm/snapshot/${date}/`);
      setSnapshot(data);
    } catch {
      setSnapshot(null);
    }
  }

  return (
    <div className="my-3">
      <h5>Swarm Snapshot</h5>
      <div className="d-flex gap-2 mb-2">
        <input
          type="date"
          className="form-control"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
        <button className="btn btn-sm btn-primary" onClick={fetchSnapshot}>
          View
        </button>
      </div>
      {snapshot && (
        <div>
          <h6>Agents</h6>
          <ul className="list-unstyled">
            {snapshot.agents.map((a) => (
              <li key={a.id}>{a.name}</li>
            ))}
          </ul>
          <h6>Clusters</h6>
          <ul className="list-unstyled">
            {snapshot.clusters.map((c) => (
              <li key={c.id}>{c.name}</li>
            ))}
          </ul>
          <h6>Memory Entries</h6>
          <ul className="list-unstyled">
            {snapshot.memories.map((m) => (
              <li key={m.id}>{m.title}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
