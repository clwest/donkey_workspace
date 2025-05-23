import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ProjectQuickCreate({ onCreated }) {
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!title.trim()) return;

    setLoading(true);
    try {
      const data = await apiFetch("/assistants/projects/", {
        method: "POST",
        body: { title },
      });
      setTitle("");
      if (onCreated) onCreated(data);
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