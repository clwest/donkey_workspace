import { useState } from "react";

export default function ProjectQuickCreate({ onCreated }) {
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!title.trim()) return;

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/assistants/projects/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title }),
      });
      const data = await res.json();
      if (res.ok) {
        setTitle("");
        if (onCreated) onCreated(data); // 🔥 Callback if you want to refresh or auto-select
      } else {
        alert("Failed to create project.");
      }
    } catch (err) {
      console.error(err);
      alert("Error creating project.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="d-flex gap-2 mb-4">
      <input
        type="text"
        className="form-control"
        placeholder="New project title..."
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        disabled={loading}
      />
      <button className="btn btn-success" type="submit" disabled={loading}>
        {loading ? "Creating..." : "🚀 Create"}
      </button>
    </form>
  );
}