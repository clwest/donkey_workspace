import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function MemoryChainBuilderPage() {
  const [memories, setMemories] = useState([]);
  const [selected, setSelected] = useState([]);
  const [title, setTitle] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchMemories() {
      const res = await fetch("http://localhost:8000/api/memory/list/");
      const data = await res.json();
      setMemories(data);
    }
    fetchMemories();
  }, []);

  function toggleMemory(id) {
    setSelected(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  }

  async function handleCreateChain() {
    if (!title || selected.length === 0) {
      alert("Please enter a title and select memories.");
      return;
    }
    const res = await fetch("http://localhost:8000/api/memory/chains/create/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, memory_ids: selected }),
    });
    if (res.ok) {
      alert("✅ Memory Chain created!");
      navigate("/memories"); // Or build a chains list later
    } else {
      alert("❌ Failed to create chain");
    }
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4">🔗 Build a Memory Chain</h1>

      <input
        className="form-control mb-3"
        placeholder="Chain Title (ex: Overcoming Obstacles)"
        value={title}
        onChange={e => setTitle(e.target.value)}
      />

      <div className="list-group mb-3">
        {memories.map(memory => (
          <label key={memory.id} className="list-group-item">
            <input
              type="checkbox"
              checked={selected.includes(memory.id)}
              onChange={() => toggleMemory(memory.id)}
              className="form-check-input me-2"
            />
            {memory.event.slice(0, 100)}...
          </label>
        ))}
      </div>

      <button onClick={handleCreateChain} className="btn btn-primary">
        🚂 Create Chain
      </button>
    </div>
  );
}