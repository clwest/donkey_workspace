import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function TrainPromptsFromMemoriesPage() {
  const [memories, setMemories] = useState([]);
  const [selectedMemories, setSelectedMemories] = useState([]);
  const [trainedPrompt, setTrainedPrompt] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchMemories() {
      const res = await fetch("http://localhost:8000/api/memory/list/");
      const data = await res.json();
      setMemories(data);
    }
    fetchMemories();
  }, []);

  function toggleSelect(memoryId) {
    setSelectedMemories(prev =>
      prev.includes(memoryId)
        ? prev.filter(id => id !== memoryId)
        : [...prev, memoryId]
    );
  }

  async function handleTrain() {
    if (!selectedMemories.length) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/memory/train-prompts/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ memory_ids: selectedMemories }),
      });
      const data = await res.json();
      if (res.slug) {
        navigate(`/prompts/${data.slug}`);
      } else {
        setTrainedPrompt(data.content);
      }
    } catch (error) {
      console.error("Failed to train prompt", error);
      alert("Training failed!");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container my-5">
      <h1>🚀 Train a System Prompt from Your Memories</h1>

      <div className="my-4">
        {memories.map((memory) => (
          <div key={memory.id} className="form-check mb-2">
            <input
              type="checkbox"
              className="form-check-input"
              id={memory.id}
              checked={selectedMemories.includes(memory.id)}
              onChange={() => toggleSelect(memory.id)}
            />
            <label className="form-check-label" htmlFor={memory.id}>
              {memory.event.slice(0, 100)}...
            </label>
          </div>
        ))}
      </div>

      <button
        className="btn btn-primary mb-4"
        disabled={!selectedMemories.length || loading}
        onClick={handleTrain}
      >
        ✨ Train Prompt
      </button>

      <Link to="/memories" className="btn btn-outline-secondary ms-2">
        🔙 Back to Memories
      </Link>

      {trainedPrompt && (
        <div className="mt-5 p-4 bg-light rounded">
          <h3>📝 Trained Prompt Preview:</h3>
          <p>{trainedPrompt}</p>
        </div>
      )}
    </div>
  );
}