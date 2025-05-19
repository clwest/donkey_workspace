// src/pages/assistant/objectives/ProjectObjectivesPage.jsx

import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

export default function ProjectObjectivesPage() {
  const { projectId } = useParams();
  const [objectives, setObjectives] = useState([]);
  const [project, setProject] = useState(null);
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");

  useEffect(() => {
    async function fetchData() {
      const [projRes, objRes] = await Promise.all([
        fetch(`http://localhost:8000/api/assistants/projects/${projectId}/`),
        fetch(`http://localhost:8000/api/assistants/projects/${projectId}/objectives/`)
      ]);
      const projData = await projRes.json();
      const objData = await objRes.json();
      setProject(projData);
      setObjectives(objData);
    }
    fetchData();
  }, [projectId]);

  async function createObjective() {
    if (!newTitle.trim()) return;

    const res = await fetch(`http://localhost:8000/api/assistants/projects/${projectId}/objectives/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: newTitle, description: newDescription }),
    });

    if (res.ok) {
      const data = await res.json();
      setObjectives(prev => [data, ...prev]);
      setNewTitle("");
      setNewDescription("");
    }
  }

  async function toggleComplete(id, isCompleted) {
    await fetch(`http://localhost:8000/api/assistants/projects/${projectId}/objectives/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, is_completed: !isCompleted }),
    });

    setObjectives(prev =>
      prev.map(obj =>
        obj.id === id ? { ...obj, is_completed: !isCompleted } : obj
      )
    );
  }

  async function deleteObjective(id) {
    if (!window.confirm("Delete this objective?")) return;

    await fetch(`http://localhost:8000/api/assistants/projects/${projectId}/objectives/${id}/`, {
      method: "DELETE",
    });

    setObjectives(prev => prev.filter(obj => obj.id !== id));
  }

  async function inferObjectives() {
    if (!project?.assistant?.slug) return;
    const res = await fetch(
      `http://localhost:8000/api/assistants/${project.assistant.slug}/reflect-to-objectives/`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: projectId }),
      }
    );
    if (res.ok) {
      const data = await res.json();
      if (data.length) {
        window.alert(`Created ${data.length} objectives.`);
        setObjectives(prev => [...data, ...prev]);
      }
    } else {
      window.alert("Failed to generate objectives");
    }
  }

  if (!project) {
    return <div className="container my-5">Loading objectives...</div>;
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4">🎯 Project Objectives</h1>

      <div className="card p-3 mb-4 shadow-sm">
        <h5>Create New Objective</h5>
        <input
          type="text"
          className="form-control mb-2"
          placeholder="Objective Title"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
        />
        <textarea
          className="form-control mb-2"
          placeholder="Objective Description (optional)"
          value={newDescription}
          onChange={(e) => setNewDescription(e.target.value)}
        />
        <button onClick={createObjective} className="btn btn-success me-2">
          ➕ Add Objective
        </button>
        <button onClick={inferObjectives} className="btn btn-outline-primary">
          🔍 Infer Objectives From Thoughts
        </button>
      </div>

      <ul className="list-group">
        {objectives.map((objective) => (
          <li
            key={objective.id}
            className="list-group-item d-flex justify-content-between align-items-center"
          >
            <div>
              <h5 className={objective.is_completed ? "text-success" : ""}>
                {objective.title}
              </h5>
              {objective.description && (
                <p className="small text-muted mb-1">{objective.description}</p>
              )}
            </div>
            <div className="d-flex gap-2">
              <button
                onClick={() => toggleComplete(objective.id, objective.is_completed)}
                className={`btn btn-${objective.is_completed ? "secondary" : "primary"} btn-sm`}
              >
                {objective.is_completed ? "Mark Incomplete" : "Mark Complete"}
              </button>
              <button
                onClick={() => deleteObjective(objective.id)}
                className="btn btn-danger btn-sm"
              >
                🗑️
              </button>
            </div>
          </li>
        ))}
      </ul>

      <div className="mt-5">
        <Link to="/assistants/projects" className="btn btn-outline-secondary">
          🔙 Back to Projects
        </Link>
      </div>
    </div>
  );
}