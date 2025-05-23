import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ReflectiveTheaterStage() {
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    apiFetch("/simulation/theater-sessions/")
      .then((res) => setSessions(res.results || res))
      .catch(() => setSessions([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Reflective Theater Sessions</h5>
      <ul className="list-group">
        {sessions.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.viewer_identity}
          </li>
        ))}
        {sessions.length === 0 && (
          <li className="list-group-item text-muted">No theater sessions.</li>
        )}
      </ul>
    </div>
  );
}
