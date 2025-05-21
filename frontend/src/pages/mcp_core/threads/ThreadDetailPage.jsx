import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import TagBadge from "../../../components/TagBadge";
import { Spinner } from "react-bootstrap";
import RefocusPromptCard from "../../../components/mcp_core/RefocusPromptCard";
import LongTermObjectiveEditor from "../../../components/mcp_core/LongTermObjectiveEditor";
import MilestoneTimeline from "../../../components/mcp_core/MilestoneTimeline";
import ObjectiveReflectionLog from "../../../components/mcp_core/ObjectiveReflectionLog";
import LinkedChainList from "../../../components/memory/LinkedChainList";
// <<<<<<< codex/add-healing-suggestions-for-low-continuity-threads
// =======
// // <<<<<<< codex/add-thread-continuity-diagnostics
// // import ThreadDiagnosticsPanel from "../../../components/mcp_core/ThreadDiagnosticsPanel";
// // =======
// // // >>>>>>> main
// // >>>>>>> main
// >>>>>>> main

export default function ThreadDetailPage() {
  const { id } = useParams();
  const [thread, setThread] = useState(null);
  const [loading, setLoading] = useState(true);
  const [chains, setChains] = useState(null);
// <<<<<<< codex/add-healing-suggestions-for-low-continuity-threads
//   const [diagnostic, setDiagnostic] = useState(null);
// =======
//   const [diag, setDiag] = useState(null);
// >>>>>>> main

  useEffect(() => {
    const fetchThread = async () => {
      try {
        const data = await apiFetch(`/mcp/threads/${id}/`);
        setThread(data);
        console.log(data)
      } catch (err) {
        console.error("Failed to load thread:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchThread();
    apiFetch(`/mcp/threads/${id}/diagnose/`).then(setDiagnostic).catch(() => {});
  }, [id]);

  const handleDiagnostic = async () => {
    try {
      const data = await apiFetch(`/mcp/threads/${id}/diagnose/`, { method: "POST" });
      setDiag(data);
      setThread({ ...thread, continuity_score: data.score, last_diagnostic_run: new Date().toISOString() });
    } catch (err) {
      console.error("Diagnostic failed", err);
    }
  };

  useEffect(() => {
    apiFetch(`/memory/threads/${id}/linked_chains/`)
      .then(setChains)
      .catch(() => {});
  }, [id]);

  if (loading) return <Spinner className="m-5" animation="border" />;
  if (!thread) return <div className="container my-5">❌ Thread not found.</div>;

  return (
    <div className="container my-5">
      <h2 className="mb-2">{thread.title}</h2>
      <div className="text-muted mb-3">
        Created: {new Date(thread.created_at).toLocaleString()}
      </div>

      {thread.summary && (
        <p className="lead" style={{ whiteSpace: "pre-line" }}>
          {thread.summary}
        </p>
      )}

      {diagnostic && diagnostic.refocus_prompt && (
        <RefocusPromptCard prompt={diagnostic.refocus_prompt} />
      )}

      {diagnostic && diagnostic.continuity_score < 0.5 && (
        <button
          className="btn btn-warning mb-3"
          onClick={async () => {
            const data = await apiFetch(`/mcp/threads/${id}/refocus/`, { method: "POST" });
            setDiagnostic({ ...diagnostic, refocus_prompt: data.prompt });
          }}
        >
          🩹 Suggest Refocus
        </button>
      )}

      <h5 className="mt-4">🎯 Long Term Objective</h5>
      <LongTermObjectiveEditor thread={thread} onUpdated={setThread} />

      {thread.milestones && thread.milestones.length > 0 && (
        <div className="mt-3">
          <h6>Milestones</h6>
          <MilestoneTimeline milestones={thread.milestones} />
        </div>
      )}

      <div className="mt-3">
        <button
          className="btn btn-outline-primary mb-2"
          onClick={async () => {
            await apiFetch(`/mcp/threads/${id}/reflect/`, { method: "POST" });
            const data = await apiFetch(`/mcp/threads/${id}/objective/`);
            setThread({ ...thread, milestones: data.milestones });
          }}
        >
          Reflect on Objective Progress
        </button>
        <ObjectiveReflectionLog threadId={id} />
      </div>

      {thread.tags && thread.tags.length > 0 && (
        <div className="mb-3">
          <strong>Tags:</strong>{" "}
          {thread.tags.map((tag) => (
            <TagBadge key={tag.slug} tag={tag} className="me-1" />
          ))}
        </div>
      )}

      {thread.origin_memory?.text && (
        <div className="alert alert-light border-start border-4 border-primary">
          <h6 className="mb-1">🧠 Origin Memory</h6>
          <p className="mb-0 small">
            <em>{thread.origin_memory.text}</em>
          </p>
          <div className="text-muted small mt-1">
            {new Date(thread.origin_memory.created_at).toLocaleString()}
          </div>
        </div>
      )}

      {thread.related_memory_previews?.length > 0 && (
        <div className="mt-4">
          <h5>🧠 Related Memories</h5>
          <ul className="list-group">
            {thread.related_memory_previews.map((mem) => (
              <li key={mem.id} className="list-group-item">
                <Link to={`/memories/${mem.id}`} className="fw-bold">
                  {mem.preview.length > 100
                    ? mem.preview.slice(0, 100) + "..."
                    : mem.preview}
                </Link>
                <div className="text-muted small">
                  {new Date(mem.created_at).toLocaleString()}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {chains && (
        <div className="mt-4">
          <h5>🔗 Linked Memory Chains</h5>
          <LinkedChainList chains={chains} />
        </div>
      )}

      <ThreadDiagnosticsPanel thread={thread} />
      <button className="btn btn-primary mb-3" onClick={handleDiagnostic}>
        Run Diagnostic
      </button>

      <div className="mt-4">
        <Link to="/threads" className="btn btn-outline-secondary">
          ← Back to Threads
        </Link>
      </div>
    </div>
  );
}