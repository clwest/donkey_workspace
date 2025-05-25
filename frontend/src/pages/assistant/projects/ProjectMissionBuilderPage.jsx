import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";

export default function ProjectMissionBuilderPage() {
  const { id } = useParams(); // project ID
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [mission, setMission] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!id) {
      console.warn("ProjectMissionBuilderPage: missing project id");
      return;
    }
    async function fetchProject() {
      try {
        const res = await fetch(`/api/assistants/projects/${id}/`);
        const data = await res.json();
        setProject(data);
      } catch (err) {
        console.error("Failed to load project", err);
      }
    }
    fetchProject();
  }, [id]);

  async function handleGenerateMission() {
    setLoading(true);
    try {
      const res = await fetch(`/api/assistants/projects/generate-mission/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: id }),
      });
      const data = await res.json();
      setMission(data.mission);
    } catch (error) {
      console.error("Mission generation failed", error);
    } finally {
      setLoading(false);
    }
  }

  if (!project) return <div className="container my-5">Loading project details...</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-4">🚀 Define Project Mission</h1>
      <h3 className="text-muted mb-4">{project.title}</h3>

      <div className="mb-5">
        <button
          onClick={handleGenerateMission}
          className="btn btn-primary"
          disabled={loading}
        >
          ✨ Generate Mission
        </button>
        <Link to="/assistants/projects" className="btn btn-outline-secondary ms-2">
          🔙 Back to Projects
        </Link>
      </div>

      {mission && (
        <div className="p-4 bg-light rounded">
          <h4>🧭 Project Mission:</h4>
          <p>{mission}</p>
        </div>
      )}
    </div>
  );
}