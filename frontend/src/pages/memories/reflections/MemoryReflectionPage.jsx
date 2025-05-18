// src/pages/memory/MemoryReflectionPage.jsx
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import '../styles/MemoryReflectionPage.css'

export default function MemoryReflectionPage() {
  const [memories, setMemories] = useState([]);
  const [selected, setSelected] = useState([]);
  const [reflection, setReflection] = useState("");
  const [title, setTitle] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchMemories() {
      const res = await fetch("http://localhost:8000/api/memory/list/");
      const data = await res.json();
      setMemories(data.filter(m => m.is_conversation)); // Only show convo memories
    }
    fetchMemories();
  }, []);

  function handleSelect(id) {
    setSelected(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  }

  async function generateReflection() {
    if (selected.length === 0) return alert("Select at least one memory.");
    const res = await fetch("http://localhost:8000/api/memory/reflect/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ memory_ids: selected }),
    });
    const data = await res.json();
    setReflection(data.summary);
    setTitle("Reflection on " + new Date().toLocaleDateString());
  }

  async function saveReflection() {
    if (!title || !reflection) return alert("Please enter title and summary.");
    const res = await fetch("http://localhost:8000/api/memory/reflection/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        summary: reflection,
        memory_ids: selected,
      }),
    });
    if (res.ok) {
      alert("Reflection saved!");
      navigate("/memories");
    } else {
      alert("Failed to save reflection.");
    }
  }

  return (
    <div className="container py-5">
      <h1 className="mb-4">🧠 Reflect on Your Memories</h1>

      {memories.length === 0 ? (
        <p className="text-muted">No memory conversations found yet. Try chatting with an assistant first.</p>
      ) : (
        <div className="row row-cols-1 row-cols-md-2 g-4 mb-4">
          {memories.map((m) => (
            <div key={m.id} className="col">
              <div className={`card h-100 ${selected.includes(m.id) ? 'border-primary' : ''}`}>
                <div className="card-body">
                  <div className="form-check mb-2">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      checked={selected.includes(m.id)}
                      onChange={() => handleSelect(m.id)}
                      id={`memory-${m.id}`}
                    />
                    <label className="form-check-label fw-bold" htmlFor={`memory-${m.id}`}>
                      🧠 Conversation with {m.assistant_name || "Unknown"}
                    </label>
                  </div>
                  <p className="card-text">
                    {m.event.length > 160 ? m.event.slice(0, 160) + "..." : m.event}
                  </p>
                  <small className="text-muted">
                    Saved {new Date(m.created_at).toLocaleDateString()}
                  </small>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="d-flex gap-3 mb-4">
        <button className="btn btn-primary" onClick={generateReflection}>
          ✨ Generate Reflection
        </button>
        <Link to="/memories" className="btn btn-outline-secondary">
          ← Back to Memories
        </Link>
      </div>

      {reflection && (
        <>
          <div className="mb-3">
            <label className="form-label fw-bold">📝 Reflection Title</label>
            <input
              className="form-control"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="mb-3">
            <label className="form-label fw-bold">💭 Reflection Summary</label>
            <textarea
              className="form-control"
              style={{ height: "200px" }}
              value={reflection}
              onChange={(e) => setReflection(e.target.value)}
            />
          </div>

          <button className="btn btn-success" onClick={saveReflection}>
            💾 Save Reflection
          </button>
        </>
      )}
    </div>
  );
}