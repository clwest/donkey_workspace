import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import { Link } from "react-router-dom";

const AssistantProjectListByAssistant = () => {
  const { slug } = useParams();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [assistant, setAssistant] = useState(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const projectRes = await apiFetch(
          `/api/assistants/${slug}/projects/`
        );
        setProjects(projectRes);

        const assistantRes = await apiFetch(`/api/assistants/${slug}/`);
        setAssistant(assistantRes);
      } catch (err) {
        console.error("Failed to load assistant projects", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, [slug]);

  if (loading) return <p>Loading...</p>;

  return (
    <div className="container py-4">
      <h2 className="text-2xl font-semibold mb-4">\        Projects for {assistant?.name || "Unknown Assistant"}
      </h2>

      {projects.length === 0 ? (
        <p>No projects linked to this assistant yet.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {projects.map((project) => (
            <div
              key={project.id}
              className="border rounded-xl p-4 shadow-sm bg-white"
            >
              <h3 className="text-lg font-bold mb-1">{project.title}</h3>
              <p className="text-sm text-muted mb-2">\                {project.description || "No description"}
              </p>
              <div className="flex gap-2">
                <Link
                  to={`/assistants/projects/${project.slug}`}
                  className="bg-blue-600 text-white px-3 py-1 rounded-md"
                >
                  Open
                </Link>
                <Link
                  to={`/assistants/projects/${project.slug}/edit`}
                  className="border px-3 py-1 rounded-md"
                >
                  Edit
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AssistantProjectListByAssistant;
