import { useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function MilestoneQuickCreate({ projectId, onCreated }) {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ title: "", description: "" });
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    const res = await apiFetch(`/assistants/projects/${projectId}/milestones/`, {
      method: "POST",
      body: formData,
    });

    if (res.ok) {
      const data = await res.json();
      setFormData({ title: "", description: "" });
      setShowForm(false);
      onCreated?.(data);
    } else {
      alert("Failed to create milestone.");
    }
    setLoading(false);
  }

  if (!showForm) {
    return (
      <button onClick={() => setShowForm(true)} className="btn btn-success">
        ➕ Quick Create Milestone
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="bg-light p-3 rounded shadow-sm mb-4">
      <div className="mb-2">
        <input
          name="title"
          className="form-control"
          placeholder="Milestone title"
          value={formData.title}
          onChange={handleChange}
          required
        />
      </div>
      <div className="mb-2">
        <textarea
          name="description"
          className="form-control"
          placeholder="Optional description"
          value={formData.description}
          onChange={handleChange}
          rows="2"
        />
      </div>
      <div className="d-flex gap-2">
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Saving..." : "Save"}
        </button>
        <button
          type="button"
          onClick={() => setShowForm(false)}
          className="btn btn-outline-secondary"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}