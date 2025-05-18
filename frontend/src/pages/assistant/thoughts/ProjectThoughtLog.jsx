// src/pages/assistant/thoughts/ProjectThoughtLog.jsx

import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import ThoughtsPanel from "../../../components/assistant/thoughts/ThoughtsPanel";
import { toast } from "react-toastify";

export default function ProjectThoughtLog() {
  const { id } = useParams();
  const [thoughts, setThoughts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchThoughts();
  }, [id]);

  async function fetchThoughts() {
    try {
      const res = await fetch(`http://localhost:8000/api/assistants/projects/${id}/thoughts/`);
      const data = await res.json();
      setThoughts(data);
    } catch (err) {
      console.error("Failed to load thoughts", err);
      toast.error("❌ Failed to load thoughts");
    } finally {
      setLoading(false);
    }
  }

  async function handleAdd(thoughtText) {
    try {
      const res = await fetch(`http://localhost:8000/api/assistants/projects/${id}/thoughts/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thought: thoughtText }),
      });
      const data = await res.json();
      setThoughts(prev => [data, ...prev]);
    } catch (err) {
      toast.error("❌ Failed to add thought");
    }
  }

  async function handleUpdate(thoughtId, newText) {
    try {
      const res = await fetch(`http://localhost:8000/api/assistants/projects/${id}/thoughts/${thoughtId}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thought: newText }),
      });
      const data = await res.json();
      setThoughts(prev =>
        prev.map(t => (t.thought_id === thoughtId ? { ...t, thought: data.updated_text } : t))
      );
    } catch (err) {
      toast.error("❌ Failed to update thought");
    }
  }

  async function handleDelete(thoughtId) {
    try {
      await fetch(`http://localhost:8000/api/assistants/projects/${id}/thoughts/${thoughtId}/`, {
        method: "DELETE",
      });
      setThoughts(prev => prev.filter(t => t.thought_id !== thoughtId));
    } catch (err) {
      toast.error("❌ Failed to delete thought");
    }
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4">🧠 Project Thought Log</h1>
      <ThoughtsPanel
        thoughts={thoughts}
        loading={loading}
        onAdd={handleAdd}
        onUpdate={handleUpdate}
        onDelete={handleDelete}
      />
      <Link to={`/assistant/projects/${id}`} className="btn btn-outline-secondary mt-4">
        🔙 Back to Project
      </Link>
    </div>
  );
}
