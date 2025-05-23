import { useEffect, useState } from "react";
import { fetchMemoryBroadcasts } from "../../api/agents";

export default function MemoryBroadcastPanel() {
  const [broadcasts, setBroadcasts] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchMemoryBroadcasts();
        setBroadcasts(data.results || data);
      } catch (err) {
        console.error("Failed to load broadcasts", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Memory Broadcasts</h5>
      <ul className="list-group">
        {broadcasts.map((b) => (
          <li key={b.id} className="list-group-item">
            {b.name} – {b.broadcast_status}
          </li>
        ))}
        {broadcasts.length === 0 && (
          <li className="list-group-item text-muted">No broadcasts.</li>
        )}
      </ul>
    </div>
  );
}

