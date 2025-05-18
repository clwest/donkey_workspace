import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";


export default function AssistantMemoriesPage() {
  const { slug } = useParams();
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchMemories() {
      try {
        const data = await apiFetch(`/assistants/${slug}/memories/`);
        console.log(data)
        // const data = await res.json();
        setMemories(data);
      } catch (err) {
        console.error("Error fetching assistant memories:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchMemories();
  }, [slug]);

  if (loading) return <div className="container my-5">Loading assistant memories...</div>;

  return (
    <div className="container my-5">
      <h2 className="mb-4">🧠 Memories for Assistant: <span className="text-primary">{slug}</span></h2>

      {memories.length === 0 ? (
        <p>No linked memories found for this assistant.</p>
      ) : (
        <div className="list-group">
          {memories.map((memory) => (
            <Link
              key={memory.id}
              to={`/memories/${memory.id}`}
              className="list-group-item list-group-item-action"
            >
              <strong>{memory.event?.slice(0, 60) || "Untitled Memory"}</strong>
              <br />
              <small className="text-muted">
                Saved on {new Date(memory.created_at).toLocaleString()}
              </small>
            </Link>
          ))}
        </div>
      )}

      <div className="mt-4">
        <Link to={`/assistants/${slug}`} className="btn btn-outline-secondary">
          🔙 Back to Assistant
        </Link>
      </div>
    </div>
  );
}