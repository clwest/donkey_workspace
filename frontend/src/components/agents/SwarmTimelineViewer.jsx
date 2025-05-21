
import { useState, useEffect } from "react";

import apiFetch from "../../utils/apiClient";

export default function SwarmTimelineViewer() {
  const [date, setDate] = useState("");
  const [snapshot, setSnapshot] = useState(null);


  const fetchSnapshot = (d) => {
    if (!d) return;
    apiFetch(`/swarm-snapshot/${d}/`)
      .then(setSnapshot)
      .catch(() => setSnapshot(null));
  };

  useEffect(() => {
    if (date) fetchSnapshot(date);
  }, [date]);

  return (
    <div className="my-4">
      <div className="mb-3">

        <input
          type="date"
          className="form-control"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />

      </div>
      {snapshot && (
        <div>
          <h5>Agents</h5>
          <ul className="mb-3">

            {snapshot.agents.map((a) => (
              <li key={a.id}>{a.name}</li>
            ))}
          </ul>

          <h5>Clusters</h5>
          <ul className="mb-3">

            {snapshot.clusters.map((c) => (
              <li key={c.id}>{c.name}</li>
            ))}
          </ul>

          <h5>Memories</h5>
          <ul>

            {snapshot.memories.map((m) => (
              <li key={m.id}>{m.title}</li>
            ))}
          </ul>

          <button className="btn btn-sm btn-outline-secondary mt-2">
            Reflect on this snapshot
          </button>

        </div>
      )}
    </div>
  );
}
