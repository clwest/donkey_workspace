import { useEffect, useState } from "react";
import { fetchArenaActive } from "../../api/agents";

export default function SwarmArenaLiveView() {
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    fetchArenaActive()
      .then(setSessions)
      .catch(() => setSessions([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Execution Arena</h5>
      <ul className="list-group">
        {sessions.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.assistant} - {s.status}
          </li>
        ))}
        {sessions.length === 0 && (
          <li className="list-group-item text-muted">No sessions</li>
        )}
      </ul>
    </div>
  );
}
