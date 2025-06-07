import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "@/utils/apiClient";

export default function ProjectDetailPage() {
  const { id } = useParams();
  const [project, setProject] = useState(null);

  useEffect(() => {
    async function fetchProject() {
      const data = await apiFetch(`/assistants/projects/${id}/`);
      setProject(data);
    }
    fetchProject();
  }, [id]);

  if (!project) return <div className="container my-5">Loading project...</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-3">{project.title}</h1>
      <p className="text-muted">{project.description || "No description."}</p>
      {project.created_from_memory && (
        <p className="text-success">
          🧠 Spawned from memory: {project.created_from_memory}
        </p>
      )}
    </div>
  );
}