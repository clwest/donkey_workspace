import { useState } from 'react';
import apiFetch from '@/utils/apiClient';

export default function ReflectionPage() {
  const [reflection, setReflection] = useState(null);
  const [reflectionSummary, setReflectionSummary] = useState("");
  const [reflectionId, setReflectionId] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleReflect = async () => {
    setLoading(true);
    setError("");

    try {
      const data = await apiFetch('/mcp/reflect/', {
        method: 'POST',
        body: { limit: 5 },
      });

      // ✅ Update all states properly
      setReflection(data);
      setReflectionSummary(data.llm_summary);
      // Some endpoints returned {id} but older clients expected {reflection_id}
      setReflectionId(data.id || data.reflection_id);

    } catch (err) {
      console.error('Reflection error:', err);
      setError('Something went wrong during reflection.');
    } finally {
      setLoading(false);
    }
  };

  const handleExpandReflection = async () => {
    if (!reflectionId) return;  // ✅ Check reflectionId not just reflection
  
    setLoading(true);
    try {
      const data = await apiFetch(`/mcp/reflections/${reflectionId}/expand/`, {
        method: 'POST',
      });

      if (data) {
        setReflection(prev => ({
          ...prev,
          llm_summary: data.updated_summary,
        }));
        setReflectionSummary(data.updated_summary); // ✅ If you want to update summary state too
        alert("Reflection expanded successfully! 🧠⚡");
      } else {
        alert("Failed to expand reflection.");
      }
    } catch (err) {
      console.error(err);
      alert("Error expanding reflection.");
    } finally {
      setLoading(false);
    }
  };

  const saveReflection = async () => {
    if (!reflectionId) return;

    setIsSaving(true);
    try {
      const res = await apiFetch(`/mcp/reflections/${reflectionId}/save/`, {
        method: 'POST',
      });

      if (res) {
        alert("Reflection saved successfully! 🎉");
      } else {
        alert("Failed to save reflection.");
      }
    } catch (error) {
      console.error(error);
      alert("Error while saving reflection.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="container mt-5">
      <h1 className="mb-4">🧠 Assistant Reflection</h1>
      
      <div style={{ marginTop: "2rem" }}>
        <button onClick={handleReflect} className="btn btn-primary" style={{ marginRight: "1rem" }}>
          Reflect Now
        </button>
        {reflectionSummary && (
          <button onClick={saveReflection} className="btn btn-success" disabled={isSaving}>
            {isSaving ? "Saving..." : "💾 Save Reflection"}
          </button>
        )}
      </div>

      <button
        className="btn btn-warning"
        onClick={handleExpandReflection}
        disabled={loading}
        style={{ marginTop: "1rem" }}
      >
        🔄 Expand Reflection
      </button>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {reflection && (
        <div className="card mt-4">
          <div className="card-body">
            <h5 className="card-title">Raw Summary</h5>
            <pre className="card-text">{reflection.raw_summary}</pre>

            <h5 className="card-title mt-4">LLM Reflection</h5>
            <p className="card-text">{reflection.llm_summary}</p>
          </div>
        </div>
      )}
    </div>
  );
}