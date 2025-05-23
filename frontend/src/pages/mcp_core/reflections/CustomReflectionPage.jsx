// frontend/pages/mcp_core/reflections/CustomReflectionPage.jsx

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import GlobalSuccessModal from "../../../components/GlobalSuccessModal";

export default function CustomReflectionPage() {
  const [goal, setGoal] = useState("");
  const [memories, setMemories] = useState([]);
  const [selectedMemories, setSelectedMemories] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [reflecting, setReflecting] = useState(false);

  // Modal state
  const [showSuccess, setShowSuccess] = useState(false);
  const [successLink, setSuccessLink] = useState("");
  const [successTitle, setSuccessTitle] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:8000/api/mcp/memories/')
      .then(res => res.json())
      .then(data => {
        // API returns paginated results under `results`
        const results = Array.isArray(data) ? data : data.results;
        setMemories(results || []);
      });
  }, []);

  const toggleMemorySelection = (id) => {
    setSelectedMemories(prev =>
      prev.includes(id) ? prev.filter(m => m !== id) : [...prev, id]
    );
  };

  const handleReflectNow = async () => {
    if (selectedMemories.length === 0) {
      toast.warn("Please select at least one memory!");
      return;
    }

    setReflecting(true);

    try {
      const response = await fetch('http://localhost:8000/api/mcp/reflect/custom/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          memory_ids: selectedMemories,
          goal: goal.trim() || undefined,
        }),
      });

      if (response.ok) {
        const data = await response.json();

        // Show Global Success Modal
        setSuccessTitle("Custom Reflection Created! 🎯");
        setSuccessMessage("Your custom reflection is ready.");
        setSuccessLink(`/reflections/${data.id || data.reflection_id}`);
        setShowSuccess(true);

      } else {
        toast.error("Failed to create reflection.");
      }
    } catch (err) {
      console.error(err);
      toast.error("Unexpected error occurred.");
    } finally {
      setReflecting(false);
    }
  };

  const handleClearSearch = () => {
    setSearchTerm("");
  };

  const filteredMemories = memories.filter((memory) =>
    memory.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="container mt-5">
      <h1 className="mb-4">🧠 Create Custom Reflection</h1>

      <div className="mb-4">
        <label className="form-label">Optional Goal for Reflection:</label>
        <textarea
          className="form-control"
          placeholder="e.g., Identify productivity patterns..."
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          rows={3}
        />
      </div>

      <div className="mb-4">
        <div className="d-flex align-items-center mb-2">
          <label htmlFor="searchMemories" className="form-label me-3">Search Memories</label>
          {searchTerm && (
            <button onClick={handleClearSearch} className="btn btn-sm btn-outline-secondary">
              Clear Search
            </button>
          )}
        </div>
        <div className="input-group">
          <span className="input-group-text">🔎</span>
          <input
            id="searchMemories"
            type="text"
            className="form-control"
            placeholder="Type keywords to filter memories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <h5>Select Memories ({selectedMemories.length} {selectedMemories.length === 1 ? "memory" : "memories"} selected)</h5>

      {filteredMemories.length === 0 ? (
        <p>No memories match your search.</p>
      ) : (
        <div className="list-group mb-4" style={{ maxHeight: "400px", overflowY: "auto" }}>
          {filteredMemories.map(memory => (
            <label key={memory.id} className="list-group-item">
              <input
                type="checkbox"
                className="form-check-input me-2"
                checked={selectedMemories.includes(memory.id)}
                onChange={() => toggleMemorySelection(memory.id)}
              />
              {memory.content}
            </label>
          ))}
        </div>
      )}

      <button 
        onClick={handleReflectNow} 
        className="btn btn-primary mt-3"
        disabled={reflecting}
      >
        {reflecting ? "Reflecting..." : "Reflect Now"}
      </button>

      {/* 🔥 GLOBAL SUCCESS MODAL */}
      <GlobalSuccessModal
        show={showSuccess}
        onClose={() => setShowSuccess(false)}
        title={successTitle}
        message={successMessage}
        linkTo={successLink}
        linkLabel="View Reflection"
      />
    </div>
  );
}