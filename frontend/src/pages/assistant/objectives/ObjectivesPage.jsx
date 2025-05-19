import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function ObjectivesPage() {
  const { slug } = useParams();
  const [objectives, setObjectives] = useState([]);

  useEffect(() => {
    if (!slug) return;
    async function fetchObjectives() {
      try {
        const data = await apiFetch(`/assistants/${slug}/objectives/`);
        setObjectives(data);
      } catch (err) {
        console.error("Failed to load objectives", err);
      }
    }
    fetchObjectives();
  }, [slug]);

  if (!slug) {
    return <div className="container my-5">Assistant slug missing.</div>;
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4">🎯 Objectives for {slug}</h1>
      {objectives.length === 0 ? (
        <p>No objectives found.</p>
      ) : (
        <ul className="list-group mb-4">
          {objectives.map((obj) => (
            <li key={obj.id} className="list-group-item">
              <strong>{obj.title}</strong>
              {obj.description && (
                <div className="small text-muted">{obj.description}</div>
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
