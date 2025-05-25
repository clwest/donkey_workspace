import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { toast } from "react-toastify";

export default function ProjectTaskBuilderPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerateTasks() {
    setLoading(true);
    setError("");

    try {
      const res = await fetch(`/api/assistants/projects/${id}/generate_tasks/`, {
        method: "POST",
      });

      if (!res.ok) {
        const data = await res.json();
        setError(data.error || "Something went wrong");
        toast.error("❌ Failed to generate tasks.");
        return;
      }

      toast.success("✅ Tasks generated!");
      navigate(`/assistants/projects/${id}`);
    } catch (err) {
      console.error(err);
      setError("Server error.");
      toast.error("🚨 Server error while generating tasks.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4">🛠️ Task Builder</h1>

      <p className="text-muted mb-4">
        Generate a task breakdown for this project automatically.
      </p>

      <div className="d-flex gap-2">
        <button
          className="btn btn-primary"
          onClick={handleGenerateTasks}
          disabled={loading}
        >
          {loading ? "Generating Tasks..." : "🚀 Auto-Build Tasks"}
        </button>
        <Link to={`/assistants/projects/${id}`} className="btn btn-outline-secondary">
          🔙 Back to Project
        </Link>
      </div>

      {error && (
        <div className="alert alert-danger mt-4">
          {error}
        </div>
      )}
    </div>
  );
}