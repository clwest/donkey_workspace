import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import TagBadge from "../../../components/TagBadge";
import { Spinner } from "react-bootstrap";
import LongTermObjectiveEditor from "../../../components/mcp_core/LongTermObjectiveEditor";
import MilestoneTimeline from "../../../components/mcp_core/MilestoneTimeline";
import ObjectiveReflectionLog from "../../../components/mcp_core/ObjectiveReflectionLog";

export default function ThreadDetailPage() {
  const { id } = useParams();
  const [thread, setThread] = useState(null);
  const [loading, setLoading] = useState(true);

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

      <div className="mt-4">
        <Link to="/threads" className="btn btn-outline-secondary">
          ← Back to Threads
        </Link>
      </div>
    </div>
  );
}