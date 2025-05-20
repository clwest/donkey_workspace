import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import { mutateMemory } from "../../../api/memories";

export default function AssistantMemoryPage() {
  const { slug } = useParams();
  const [memories, setMemories] = useState([]);
  const [assistant, setAssistant] = useState(null);
  const [filterMood, setFilterMood] = useState("");

  useEffect(() => {
    async function fetchAssistant() {
      try {
        const data = await apiFetch(`/assistants/${slug}/`);
        setAssistant(data);
      } catch (err) {
        console.error("Failed to fetch assistant", err);
      }
    }
    fetchAssistant();
  }, [slug]);

  useEffect(() => {
    async function fetchMemories() {
      let url = `/memory/list?assistant_slug=${slug}`;
      if (filterMood) url += `&emotion=${filterMood}`;
      const res = await apiFetch(url);
      setMemories(res);
    }
    fetchMemories();
  }, [slug, filterMood]);

  async function handleMutate(id, style) {
    try {
      const data = await mutateMemory(id, style);
      setMemories((prev) => [data, ...prev]);
    } catch (err) {
      console.error("Mutation failed", err);
      alert("Failed to refine memory");
    }
  }

  return (
    <div className="container my-5">
      <h1>🧠 Memories Linked to {slug}</h1>
      {assistant && assistant.mood_stability_index < 0.5 && (
        <div className="mb-3" style={{ maxWidth: "200px" }}>
          <select
            className="form-select form-select-sm"
            value={filterMood}
            onChange={(e) => setFilterMood(e.target.value)}
          >
            <option value="">All moods</option>
            <option value="anxious">Anxious</option>
            <option value="frustrated">Frustrated</option>
            <option value="optimistic">Optimistic</option>
            <option value="confident">Confident</option>
            <option value="neutral">Neutral</option>
          </select>
        </div>
      )}

      {memories.length === 0 ? (
        <p>No memories found for this assistant.</p>
      ) : (
        <ul className="list-group">
          {memories.map((m) => (
            <li key={m.id} className="list-group-item d-flex justify-content-between align-items-start">
              <div>
                <Link to={`/memories/${m.id}`} className="fw-bold">
                  {m.summary || m.event || "Untitled Memory"}
                </Link>
                <div className="text-muted small">{new Date(m.created_at).toLocaleString()}</div>
                {m.parent_memory && (
                  <div className="text-muted small">🧬 Refined from {m.parent_memory.slice(0,8)}</div>
                )}
              </div>
              <div className="btn-group">
                <button
                  className="btn btn-sm btn-outline-primary"
                  onClick={async () => {
                    try {
                      const res = await apiFetch("/assistants/primary/spawn-agent/", {
                        method: "POST",
                        body: { memory_id: m.id },
                      });
                      window.location.href = `/assistants/${res.assistant.slug}`;
                    } catch (err) {
                      console.error(err);
                      alert("Failed to spawn agent");
                    }
                  }}
                >
                  Spawn Agent
                </button>
                <div className="dropdown ms-2">
                  <button className="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                    Refine
                  </button>
                  <ul className="dropdown-menu">
                    <li><button className="dropdown-item" onClick={() => handleMutate(m.id, "clarify")}>Clarify</button></li>
                    <li><button className="dropdown-item" onClick={() => handleMutate(m.id, "shorten")}>Shorten</button></li>
                    <li><button className="dropdown-item" onClick={() => handleMutate(m.id, "rephrase")}>Rephrase</button></li>
                  </ul>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      <div className="mt-4">
        <Link to="/assistant-dashboard" className="btn btn-secondary">
          ⬅️ Back to Assistants
        </Link>
      </div>
    </div>
  );
}