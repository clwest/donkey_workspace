import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function ObjectivesPage() {
  const { slug } = useParams();
  const [objectives, setObjectives] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!slug) return;
    async function fetchObjectives() {
      try {
        const data = await apiFetch(`/assistants/${slug}/objectives/`);
        setObjectives(data);
      } catch (err) {
        console.error("Failed to load objectives", err);
      } finally {
        setLoading(false);
      }
    }
    fetchObjectives();
  }, [slug]);

  async function handlePlanTasks(objId) {
    try {
      await apiFetch(`/assistants/${slug}/plan-tasks/${objId}/`, { method: "POST" });
      const data = await apiFetch(`/assistants/${slug}/objectives/`);
      setObjectives(data);
    } catch (err) {
      console.error("Failed to plan tasks", err);
    }
  }

  if (!slug) {
    return <div className="container my-5">Assistant slug missing.</div>;
  }

  if (loading) return <div className="container my-5">Loading...</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-4">🎯 Objectives for {slug}</h1>
      {objectives.length === 0 ? (
        <p>No objectives found.</p>
      ) : (
        <ul className="list-group mb-4">
          {objectives.map((obj) => (
            <li key={obj.id} className="list-group-item">
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <strong>{obj.title}</strong>
                  {obj.description && (
                    <div className="small text-muted">{obj.description}</div>
                  )}
                </div>
                <button
                  className="btn btn-sm btn-outline-primary"
                  onClick={() => handlePlanTasks(obj.id)}
                >
                  ✨ Plan Tasks
                </button>
              </div>
              {obj.tasks && obj.tasks.length > 0 ? (
                <ul className="mt-2">
                  {obj.tasks.map((t) => (
                    <li key={t.id} className="small d-flex justify-content-between">
                      <span>{t.title}</span>
                      <span className="badge bg-secondary">{t.status}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="small text-muted mt-2">No tasks yet</div>
              )}
            </li>
          ))}
        </ul>
      )}

      <Link to="/assistants/projects" className="btn btn-outline-secondary">
        🔙 Back to Projects
      </Link>
    </div>
  );
}
