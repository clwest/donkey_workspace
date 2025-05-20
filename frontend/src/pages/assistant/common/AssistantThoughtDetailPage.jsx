import { useParams, Link } from "react-router-dom";
import { useEffect, useState } from "react";
import TagBadge from "../../../components/TagBadge";
import { Spinner } from "react-bootstrap";

export default function AssistantThoughtDetailPage() {
  const { slug, id } = useParams();
  const [thought, setThought] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) {
      console.warn("AssistantThoughtDetailPage: missing thought id");
      return;
    }
    const fetchThought = async () => {
      try {
        const res = await fetch(`/api/assistants/thoughts/${id}/`);
        const data = await res.json();
        setThought(data);
      } catch (err) {
        console.error("Error fetching thought:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchThought();
  }, [id]);

  if (loading) return <Spinner animation="border" className="m-5" />;
  if (!thought) return <div className="alert alert-danger">Thought not found.</div>;

  return (
    <div className="container my-5">
      <h2 className="mb-4">
        🧠 Thought Detail
        <small className="text-muted d-block fs-6 mt-1">
          {new Date(thought.created_at).toLocaleString()} | {thought.thought_type} ({thought.role})
        </small>
      </h2>

      <div className="card p-4 shadow-sm">
        <p style={{ whiteSpace: "pre-line" }}>{thought.thought}</p>

        {thought.linked_memory_preview && (
          <div className="alert alert-light mt-4">
            <strong>🧠 Linked Memory:</strong>
            <p className="mb-0" style={{ whiteSpace: "pre-line" }}>
              {thought.linked_memory_preview}
            </p>
          </div>
        )}

        {thought.tags && thought.tags.length > 0 && (
          <div className="mt-3">
            <strong className="text-muted d-block mb-2">🏷️ Tags:</strong>
            {thought.tags.map((tag, idx) => (
              <TagBadge key={idx} tag={tag} className="me-2 mb-2" />
            ))}
          </div>
        )}
      </div>

      <div className="mt-4">
        <Link to={`/assistants/${slug}/thoughts`} className="btn btn-outline-secondary">
          ← Back to Thought Log
        </Link>
      </div>
    </div>
  );
}
