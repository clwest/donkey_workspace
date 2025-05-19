import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import { mutateMemory } from "../../../api/memories";

export default function AssistantMemoryPage() {
  const { slug } = useParams();
  const [memories, setMemories] = useState([]);

  useEffect(() => {
    async function fetchMemories() {
      const res = await apiFetch(`/memory/list?assistant=${slug}`);
      setMemories(res);
    }
    fetchMemories();
  }, [slug]);

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