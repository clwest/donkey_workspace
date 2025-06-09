// frontend/components/agents/AssistantList.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import PrimaryStar from "../../../components/assistant/PrimaryStar";
import TrustBadge from "../../../components/assistant/TrustBadge";

export default function AssistantList({ assistants: propAssistants }) {
  const [assistants, setAssistants] = useState(propAssistants || []);
  const [levelFilter, setLevelFilter] = useState("all");
  const [sortDesc, setSortDesc] = useState(true);

  const handleDelete = async (slug) => {
    if (!window.confirm("Delete this assistant?")) return;
    try {
      await apiFetch(`/assistants/${slug}/`, { method: "DELETE" });
      setAssistants((prev) => prev.filter((a) => a.slug !== slug));
    } catch (err) {
      console.error("Failed to delete", err);
      alert(err.message);
    }
  };

  const handleEndUse = async (projectId, slug) => {
    if (!window.confirm("Mark assistant's project as completed?")) return;
    try {
      await apiFetch(`/assistants/projects/${projectId}/`, {
        method: "PATCH",
        body: { status: "completed" },
      });
      const updated = await apiFetch(`/assistants/${slug}/`);
      setAssistants((prev) =>
        prev.map((a) => (a.id === updated.id ? updated : a))
      );
    } catch (err) {
      console.error("Failed to end use", err);
      alert(err.message);
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

  let rows = groups.map((g) => g.parent);
  if (levelFilter !== "all") {
    rows = rows.filter((a) => a.trust_level === levelFilter);
  }
  rows.sort((a, b) =>
    sortDesc ? b.trust_score - a.trust_score : a.trust_score - b.trust_score
  );

  return (
    <div className="container mt-5">
      <h2>🧠 Available Assistants</h2>
      <div className="mb-2 d-flex">
        <select
          className="form-select w-auto me-2"
          value={levelFilter}
          onChange={(e) => setLevelFilter(e.target.value)}
        >
          <option value="all">All Levels</option>
          <option value="ready">Ready</option>
          <option value="training">In Training</option>
          <option value="needs_attention">Needs Work</option>
        </select>
        <button
          className="btn btn-sm btn-outline-secondary"
          onClick={() => setSortDesc(!sortDesc)}
        >
          Sort {sortDesc ? "▼" : "▲"}
        </button>
      </div>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Name</th>
            <th>Specialty</th>
            <th>Trust</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows.map((a) => (
            <tr key={a.id}>
              <td>
                <Link to={`/assistants/${a.slug}`}>{a.name}</Link>
                <PrimaryStar isPrimary={a.is_primary} />
              </td>
              <td>{a.specialty}</td>
              <td>
                {a.trust_score}/100{' '}
                <TrustBadge
                  label={
                    a.trust_level === 'ready'
                      ? 'trusted'
                      : a.trust_level === 'needs_attention'
                      ? 'unreliable'
                      : 'neutral'
                  }
                />
              </td>
              <td>
                <Link
                  to={`/assistants/${a.slug}/edit`}
                  className="btn btn-sm btn-outline-secondary me-2"
                >
                  ✏️ Edit
                </Link>
                <button
                  className="btn btn-sm btn-outline-danger"
                  onClick={() => handleDelete(a.slug)}
                >
                  🗑️ Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}