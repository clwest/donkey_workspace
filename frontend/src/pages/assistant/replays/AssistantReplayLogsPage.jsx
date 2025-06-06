import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";

export default function AssistantReplayLogsPage() {
  const { slug } = useParams();
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    apiFetch(`/assistants/${slug}/replays/`)
      .then((res) => setLogs(res))
      .catch(() => setLogs([]));
  }, [slug]);

  return (
    <div className="container my-5">
      <h2 className="mb-4">🌀 Reflection Replays</h2>
      <ul className="list-group mb-3">
        {logs.map((r) => (
          <li key={r.id} className="list-group-item d-flex justify-content-between align-items-start">
            <div>
              <strong>{r.original_reflection}</strong>
              <br />
              <small className="text-muted">{new Date(r.created_at).toLocaleString()}</small>
            </div>
            <span className="badge bg-secondary">
              {r.new_score?.toFixed ? r.new_score.toFixed(2) : r.new_score}
            </span>
          </li>
        ))}
        {logs.length === 0 && (
          <li className="list-group-item text-muted">No replays found.</li>
        )}
      </ul>
      <Link to={`/assistants/${slug}/reflections`} className="btn btn-outline-secondary me-2">
        🔙 Back to Reflections
      </Link>
      <Link to={`/assistants/${slug}`} className="btn btn-outline-secondary">
        Assistant Home
      </Link>
    </div>
  );
}
