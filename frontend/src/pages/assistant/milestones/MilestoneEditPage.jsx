// src/pages/assistant/milestones/MilestoneEditPage.jsx
import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";

export default function MilestoneEditPage() {
  const { projectId, milestoneId } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ title: "", description: "", due_date: "" });

  useEffect(() => {
    async function fetchMilestone() {
      const res = await fetch(`/api/assistants/projects/${projectId}/milestones/${milestoneId}/`);
      const data = await res.json();
      setFormData({ title: data.title, description: data.description, due_date: data.due_date?.split("T")[0] || "" });
    }
    fetchMilestone();
  }, [projectId, milestoneId]);

  function handleChange(e) {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const res = await fetch(`/api/assistants/projects/${projectId}/milestones/${milestoneId}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    if (res.ok) {
      navigate(`/projects/${projectId}/milestones`);
    } else {
      alert("Failed to update milestone");
    }
  }

  return (
    <div className="container my-5">
      <h1>✏️ Edit Milestone</h1>
      <form onSubmit={handleSubmit} className="mt-4">
        <div className="mb-3">
          <label className="form-label">Title</label>
          <input name="title" className="form-control" value={formData.title} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label">Description</label>
          <textarea name="description" className="form-control" value={formData.description} onChange={handleChange} />
        </div>
        <div className="mb-3">
          <label className="form-label">Due Date</label>
          <input type="date" name="due_date" className="form-control" value={formData.due_date} onChange={handleChange} />
        </div>
        <button type="submit" className="btn btn-primary">Save Changes</button>
      </form>
    </div>
  );
}