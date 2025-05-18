// src/pages/assistant/projects/ProjectsDashboardPage.jsx
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import ProjectQuickCreate from "../../../components/assistant/ProjectQuickCreate";
import "./styles/ProjectDashboardPage.css";

export default function ProjectsDashboardPage() {
  const [projects, setProjects] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchProjects() {
      const res = await fetch("http://localhost:8000/api/assistants/projects/");
      const data = await res.json();
      setProjects(data);
    }
    fetchProjects();
  }, []);

  async function deleteProject(id) {
    if (!window.confirm("Are you sure you want to delete this project?")) return;

    await fetch(`http://localhost:8000/api/assistants/projects/${id}/`, {
      method: "DELETE",
    });

    setProjects(prev => prev.filter(p => p.id !== id));
  }

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="mb-0">📋 Assistant Projects Dashboard</h1>
        <Link to="/assistants/projects/create" className="btn btn-success">
          ➕ Create New Project
        </Link>
      </div>

      <div className="mb-4">
        <ProjectQuickCreate onCreated={(project) => {
          setProjects(prev => [project, ...prev]);
        }} />
      </div>

      {projects.length === 0 ? (
        <p className="text-muted">No projects found. Start building something awesome!</p>
      ) : (
        <div className="row g-4">
          {projects.map(project => (
            <div key={project.id} className="col-md-6 col-lg-4">
              <div className="card h-100 shadow-sm project-card">
                <div className="card-body d-flex flex-column">
                  <h5 className="card-title fw-semibold">{project.title}</h5>
                  <p className="card-text text-muted small mb-3">
                    {project.description?.slice(0, 100) || "No description"}
                  </p>

                  <div className="d-flex flex-wrap gap-2 mt-auto">
                    <Link
                      to={`/assistants/projects/${project.id}`}
                      className="btn btn-primary btn-sm flex-grow-1"
                    >
                      🚀 Open
                    </Link>
                    <Link
                      to={`/assistants/projects/${project.id}/edit`}
                      className="btn btn-outline-secondary btn-sm"
                    >
                      ✏️ Edit
                    </Link>
                    <Link
                      to={`/assistants/projects/${project.id}/thoughts`}
                      className="btn btn-outline-info btn-sm flex-grow-1"
                    >
                      🧠 Thought Log
                    </Link>
                    <button
                      onClick={() => deleteProject(project.id)}
                      className="btn btn-danger btn-sm"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}