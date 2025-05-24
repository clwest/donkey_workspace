import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ReflectionPlaybackTimeline() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/simulation/swarm-reflection-playback/")
      .then((res) => setLogs(res.results || res))
      .catch(() => setLogs([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="my-3">
      <h5>Reflection Playback Timeline</h5>
      {loading && <div>Loading...</div>}
      <ul className="list-group">
        {logs.map((l) => (
          <li key={l.id} className="list-group-item">
            {l.tag || l.id}
          </li>
        ))}
        {!loading && logs.length === 0 && (
          <li className="list-group-item text-muted">No playback logs.</li>
        )}
      </ul>
    </div>
  );
}
