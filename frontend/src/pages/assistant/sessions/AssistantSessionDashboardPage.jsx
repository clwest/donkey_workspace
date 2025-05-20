import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import MemoryChainSettingsPanel from "../../../components/assistant/memory_chain/MemoryChainSettingsPanel"

export default function AssistantSessionDashboardPage({ slug: slugProp }) {
  const params = useParams();
  const slug = slugProp || params.slug;
  const [sessions, setSessions] = useState([]);
  const [delegations, setDelegations] = useState([]);
  const [threads, setThreads] = useState([]);
  const [reflection, setReflection] = useState(null);
  const [dreamText, setDreamText] = useState(null);
  const [dreamLoading, setDreamLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [projectId, setProjectId] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        if (!slug) return;
        const [sessRes, delRes, asst] = await Promise.all([
          apiFetch(`/assistants/${slug}/sessions/`),
          apiFetch(`/assistants/${slug}/delegations/`),
          apiFetch(`/assistants/${slug}/`),
        ]);
        setSessions(sessRes.sessions || []);
        setThreads(sessRes.threads || []);
        setDelegations(delRes || []);
        setProjectId(asst.current_project?.id || null);
      } catch (err) {
        console.error("Failed to load dashboard", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  const handleReflect = async () => {
    try {
      const res = await apiFetch(`/assistants/${slug}/reflect-now/`, {
        method: "POST",
      });
      setReflection(res);
    } catch (err) {
      console.error("Reflection failed", err);
    }
  };

  const handleDream = async () => {
    try {
      setDreamLoading(true);
      const res = await apiFetch(`/assistants/${slug}/dream/`, { method: "POST" });
      setDreamText(res.dream);
    } catch (err) {
      console.error("Dream failed", err);
    } finally {
      setDreamLoading(false);
    }
  };

  if (!slug)
    return <div className="container my-5">Assistant slug missing.</div>;
  if (loading) return <div className="container my-5">Loading...</div>;

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>Sessions Dashboard: {slug}</h2>
        <div>
          <Link
            to={`/assistants/${slug}`}
            className="btn btn-outline-secondary me-2"
          >
            Back
          </Link>
          <button className="btn btn-primary" onClick={handleReflect}>
            Reflect Now
          </button>
          <button
            className="btn btn-secondary ms-2"
            onClick={handleDream}
            disabled={dreamLoading}
          >
            {dreamLoading ? "Dreaming..." : "\uD83D\uDE34 Dream"}
          </button>
        </div>
      </div>

      {reflection && (
        <div className="alert alert-info">
          <pre className="mb-0">{reflection.summary}</pre>
        </div>
      )}
      {dreamText && (
        <div className="alert alert-primary dream-output">
          <pre className="mb-0">{dreamText}</pre>
        </div>
      )}

      <h4>Recent Sessions</h4>
      {sessions.length === 0 ? (
        <p>No sessions found.</p>
      ) : (
        <ul className="list-group mb-4">
          {sessions.map((s) => (
            <li key={s.session_id} className="list-group-item">
              <Link to={`/assistants/sessions/${s.session_id}`}>
                {s.session_id}
              </Link>
              <span className="text-muted ms-2">
                {new Date(s.created_at).toLocaleString()}
              </span>
            </li>
          ))}
        </ul>
      )}

      <h4>Delegation Events</h4>
      {delegations.length === 0 ? (
        <p>No delegation events.</p>
      ) : (
        <ul className="list-group mb-4">
          {delegations.map((d, idx) => (
            <li key={idx} className="list-group-item">
              <strong>
                {d.parent} ➡ {d.child}
              </strong>
              <div>{d.reason}</div>
              {d.summary && <div className="text-muted small">{d.summary}</div>}
            </li>
          ))}
        </ul>
      )}

      <h4>Active Threads</h4>
      {threads.length === 0 ? (
        <p>No active threads.</p>
      ) : (
        <ul className="list-group">
          {threads.map((t) => (
            <li key={t.id} className="list-group-item">
              <Link to={`/threads/${t.id}`}>{t.title}</Link>
            </li>
          ))}
        </ul>
      )}

      {projectId && (
        <MemoryChainSettingsPanel slug={slug} projectId={projectId} />
      )}
    </div>
  );
}
