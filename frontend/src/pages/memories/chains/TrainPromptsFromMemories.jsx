import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import apiFetch from "@/utils/apiClient";

export default function TrainPromptsFromMemoriesPage() {
  const [memories, setMemories] = useState([]);
  const [selectedMemories, setSelectedMemories] = useState([]);
  const [trainedPrompt, setTrainedPrompt] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchMemories() {
      const data = await apiFetch("/memory/list/");
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
      const data = await apiFetch("/memory/train-prompts/", {
        method: "POST",
        body: { memory_ids: selectedMemories },
      });
      if (data.slug) {
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