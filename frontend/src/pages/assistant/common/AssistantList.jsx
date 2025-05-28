// frontend/components/agents/AssistantList.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import PrimaryStar from "../../../components/assistant/PrimaryStar";

export default function AssistantList({ assistants: propAssistants }) {
  const [assistants, setAssistants] = useState(propAssistants || []);

  const handleDelete = async (slug) => {
    if (!window.confirm("Delete this assistant?")) return;
    try {
      await apiFetch(`/assistants/${slug}/`, { method: "DELETE" });
      setAssistants((prev) => prev.filter((a) => a.slug !== slug));
    } catch (err) {
      console.error("Failed to delete", err);
    }
  };

  useEffect(() => {
    if (!propAssistants) {
      apiFetch("/assistants/")
        .then(setAssistants)
        .catch((err) => console.error("Failed to fetch assistants:", err));
    } else {
      setAssistants(propAssistants);
    }
  }, [propAssistants]);

  // Group by parent
  const parentMap = {};
  assistants.forEach((a) => {
    if (!a.parent_assistant) {
      parentMap[a.id] = { parent: a, children: [] };
    }
  });

  assistants.forEach((a) => {
    if (a.parent_assistant && parentMap[a.parent_assistant]) {
      parentMap[a.parent_assistant].children.push(a);
    }
  });

  const groups = Object.values(parentMap).sort(
    (a, b) => (b.parent.is_primary ? 1 : 0) - (a.parent.is_primary ? 1 : 0)
  );

  return (
    <div className="container mt-5">
      <h2>🧠 Available Assistants</h2>
      <ul className="list-group">
        {groups.map(({ parent, children }) => (
          <li key={parent.id} className="list-group-item shadow-sm p-3">
            <Link to={`/assistants/${parent.slug}`} className="fw-bold text-decoration-none">
              {parent.name} <PrimaryStar isPrimary={parent.is_primary} />
            </Link>
            <div className="mt-1">
              <Link to={`/assistants/${parent.slug}/edit`} className="btn btn-sm btn-outline-secondary me-2">
                ✏️ Edit
              </Link>
              <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(parent.slug)}>
                🗑️ Delete
              </button>
            </div>
            <p className="text-muted mb-1">
              {parent.description || `${parent.name} (${parent.slug})`}
            </p>

            {children.length > 0 && (
              <ul className="ps-3">
                {children.map((child) => (
                  <li key={child.id} className="my-1">
                    <Link
                      to={`/assistants/${child.slug}`}
                      className="text-decoration-none"
                    >
                      {child.name}
                    </Link>
                    <span className="text-muted ms-1">({child.specialty})</span>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}