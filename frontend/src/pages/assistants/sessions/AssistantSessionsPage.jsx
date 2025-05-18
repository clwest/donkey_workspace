import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";

export default function AssistantSessionsPage() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchSessions() {
      try {
        const data = await apiFetch("/assistants/sessions/list/");
        setSessions(data);
      } catch (err) {
        setError("Failed to load sessions");
      } finally {
        setLoading(false);
      }
    }
    fetchSessions();
  }, []);

  if (loading) {
    return <div className="container my-5">Loading sessions...</div>;
  }

  if (error) {
    return <div className="container my-5 text-danger">{error}</div>;
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4">💬 Recent Assistant Sessions</h1>
      {sessions.length === 0 ? (
        <p>No sessions found.</p>
      ) : (
        <div className="list-group">
          {sessions.map((s) => (
            <Link
              key={s.id}
              to={`/assistants/sessions/${s.id}`}
              className="list-group-item list-group-item-action"
            >
              <div className="d-flex justify-content-between">
                <div>
                  <strong>{s.assistant_name}</strong>
                  {s.project_title && (
                    <span className="text-muted ms-2">({s.project_title})</span>
                  )}
                </div>
                <span className="text-muted">
                  {new Date(s.created_at).toLocaleString()}
                </span>
              </div>
              {s.tag_names && s.tag_names.length > 0 && (
                <div className="mt-1">
                  {s.tag_names.map((tag) => (
                    <span key={tag} className="badge bg-secondary me-2">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
              {s.summary && (
                <p className="mb-0 text-truncate">{s.summary}</p>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
