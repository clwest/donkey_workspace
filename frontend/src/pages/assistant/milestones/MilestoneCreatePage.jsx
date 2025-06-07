// src/pages/assistant/milestones/MilestoneCreatePage.jsx
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import apiFetch from "@/utils/apiClient";

export default function MilestoneCreatePage() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ title: "", description: "", due_date: "" });

  function handleChange(e) {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const res = await apiFetch(`/assistants/projects/${projectId}/milestones/`, {
      method: "POST",
      body: formData,
    });
    if (res) {
      navigate(`/projects/${projectId}/milestones`);
    } else {
      alert("Failed to create milestone");
    }
  }

  return (
    <div className="container my-5">
      <h1>➕ Create New Milestone</h1>
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
        <button type="submit" className="btn btn-primary">Create Milestone</button>
      </form>
    </div>
  );
}