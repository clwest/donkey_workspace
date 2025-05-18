import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";

export default function AssistantSessionDetailPage() {
  const { sessionId } = useParams();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch(`/assistants/sessions/detail/${sessionId}/`);
        setSession(data);
      } catch (err) {
        setError("Failed to load session");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [sessionId]);

  const handleCopy = () => {
    if (session?.full_transcript) {
      navigator.clipboard?.writeText(session.full_transcript);
    }
  };

  function renderTranscript() {
    if (!session?.full_transcript) return null;
    return session.full_transcript.split(/\n+/).map((line, idx) => {
      const isUser = line.toLowerCase().startsWith("user:");
      const content = line.replace(/^\w+:\s*/, "");
      const align = isUser ? "text-end" : "text-start";
      const bubble = isUser ? "bg-primary text-white" : "bg-light";
      return (
        <div key={idx} className={`my-2 ${align}`}>
          <div className={`d-inline-block p-2 rounded ${bubble}`} style={{ maxWidth: "80%" }}>
            {content}
          </div>
        </div>
      );
    });
  }

  if (loading) return <div className="container my-5">Loading...</div>;
  if (error) return <div className="container my-5 text-danger">{error}</div>;
  if (!session) return null;

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between align-items-start mb-3">
        <div>
          <h3 className="mb-1">{session.assistant_name}</h3>
          <small className="text-muted">
            {new Date(session.created_at).toLocaleString()}
          </small>
          {session.project_title && (
            <div className="small">Project: {session.project_title}</div>
          )}
          {session.tags && session.tags.length > 0 && (
            <div className="mt-2">
              {session.tags.map((t) => (
                <span key={t} className="badge bg-secondary me-2">
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="d-flex gap-2">
          <button className="btn btn-sm btn-outline-secondary" onClick={handleCopy}>
            Copy
          </button>
          <Link to="/assistants/sessions" className="btn btn-sm btn-outline-primary">
            Back
          </Link>
        </div>
      </div>
      <div>{renderTranscript()}</div>
    </div>
  );
}
