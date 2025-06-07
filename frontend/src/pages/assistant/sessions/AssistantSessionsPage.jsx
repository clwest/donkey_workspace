import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import './styles/sessions.css'

export default function AssistantSessionsPage() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const assistantSlug = params.get("assistant");
    async function fetchSessions() {
      try {
        const url = assistantSlug
          ? `/api/assistants/sessions/list/?assistant=${assistantSlug}`
          : `/api/assistants/sessions/list/`;
    
        const data = await apiFetch(url.replace('/api', ''), { allowUnauthenticated: false });
        setSessions(data);
      } catch (err) {
        console.error("Failed to load sessions", err);
      } finally {
        setLoading(false); // 👈 Add this to stop the spinner
      }
    }
    fetchSessions();
  }, []);

  if (loading) {
    return <div className="container my-5">Loading sessions...</div>;
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4">💬 Assistant Chat Sessions</h1>
      {sessions.length === 0 ? (
        <p>No sessions found.</p>
      ) : (
        <div className="list-group">
          {sessions.map((session) => (
            <Link
              key={session.session_id}
              to={`/assistants/sessions/${session.session_id}`}
              className="list-group-item list-group-item-action shadow-sm p-3"
            >
              <div className="d-flex justify-content-between">
                <strong>{session.assistant_name}</strong>
                <span className="text-muted">{new Date(session.created_at).toLocaleString()}</span>
              </div>
              <p className="mb-0 text-truncate">
                {session.message_count === 0
                  ? "No messages yet."
                  : `Sessions: ${session.message_count ?? "Unknown"}`}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}