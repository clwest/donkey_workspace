import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import apiFetch from "../../../utils/apiClient"

export default function CreateProjectPage() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [assistant, setAssistant] = useState(""); // required!
  const [assistants, setAssistants] = useState([]);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadAssistants() {
      try {
        const res = await apiFetch("/assistants/");
        setAssistants(res.results || res); // Handle both paginated and flat
      } catch (err) {
        console.error("Failed to load assistants:", err);
      }
    }
    loadAssistants();
    
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (!assistant) {
      setError("Please select an assistant for the project.");
      return;
    }

    try {
      const data = await apiFetch("/assistants/projects/", {
        method: "POST",
        body: JSON.stringify({
          title,
          description,
          assistant, // required
        }),
      });
      console.log("✅ Project created:", data);
      navigate(`/assistants/projects/${data.id}`);
    } catch (err) {
      console.error("❌ Error creating project:", err);
      setError("Failed to create project. Check inputs and try again.");
    }
  }

  return (
    <div className="container mt-4">
      <h2>Create New Assistant Project</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label>Project Title</label>
          <input
            type="text"
            className="form-control"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div className="mb-3">
          <label>Description</label>
          <textarea
            className="form-control"
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <label>Select Assistant</label>
        <select
          className="form-select"
          value={assistant}
          onChange={(e) => setAssistant(e.target.value)}
        >
          <option value="">-- Choose Assistant --</option>
          {assistants.map((a) => (
            <option key={a.id} value={a.id}>
              {a.name}
            </option>
          ))}
        </select>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}
        <button type="submit" className="btn btn-primary">
          Create Project
        </button>
      </form>
    </div>
  );
}