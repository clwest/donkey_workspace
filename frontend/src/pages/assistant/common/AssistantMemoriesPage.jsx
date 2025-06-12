import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import PlanProjectFromMemoryModal from "../../../components/assistant/PlanProjectFromMemoryModal";


export default function AssistantMemoriesPage() {
  const { slug } = useParams();
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState([]);
  const [showPlan, setShowPlan] = useState(false);

  useEffect(() => {
    async function fetchMemories() {
      try {
        const data = await apiFetch(`/assistants/${slug}/memories/`);
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
    <div className="container my-5" id="memories-panel">
      <h2 className="mb-4">🧠 Memories for Assistant: <span className="text-primary">{slug}</span></h2>

      {memories.length === 0 ? (
        <p>No linked memories found for this assistant.</p>
      ) : (
        <div className="list-group">
          {memories.map((memory) => (
            <label key={memory.id} className="list-group-item">
              <input
                type="checkbox"
                className="form-check-input me-2"
                checked={selected.includes(memory.id)}
                onChange={() =>
                  setSelected((prev) =>
                    prev.includes(memory.id)
                      ? prev.filter((id) => id !== memory.id)
                      : [...prev, memory.id]
                  )
                }
              />
              <Link to={`/memories/${memory.id}`} className="ms-2 text-decoration-none">
                <strong>{memory.title || memory.summary?.slice(0, 60) || memory.event?.slice(0, 60) || "Untitled Memory"}</strong>
                <br />
                <small className="text-muted">
                  Saved on {new Date(memory.created_at).toLocaleString()}
                </small>
              </Link>
            </label>
          ))}
        </div>
      )}

      <div className="mt-4 d-flex gap-2">
        <button
          className="btn btn-primary"
          disabled={selected.length === 0}
          onClick={() => setShowPlan(true)}
        >
          🧠 Plan Project From Memory
        </button>
        <Link to={`/assistants/${slug}`} className="btn btn-outline-secondary">
          🔙 Back to Assistant
        </Link>
      </div>

      <PlanProjectFromMemoryModal
        slug={slug}
        memoryIds={selected}
        show={showPlan}
        onClose={() => {
          setShowPlan(false);
          setSelected([]);
        }}
      />
    </div>
  );
}