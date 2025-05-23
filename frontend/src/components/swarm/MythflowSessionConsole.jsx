import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythflowSessionConsole() {
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    apiFetch("/simulation/mythflow-sessions/")
      .then((res) => setSessions(res.results || res))
      .catch(() => setSessions([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Mythflow Sessions</h5>
      <ul className="list-group">
        {sessions.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.session_name}
          </li>
        ))}
        {sessions.length === 0 && (
          <li className="list-group-item text-muted">No sessions.</li>
        )}
      </ul>
    </div>
  );
}
