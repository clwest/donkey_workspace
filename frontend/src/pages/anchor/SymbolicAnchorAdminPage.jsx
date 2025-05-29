import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SymbolicAnchorAdminPage() {
  const [anchors, setAnchors] = useState([]);
  const [savingId, setSavingId] = useState(null);

  useEffect(() => {
    apiFetch("/memory/symbolic-anchors/")
      .then((d) => setAnchors(d.results || d))
      .catch(() => setAnchors([]));
  }, []);

  const handleChange = (id, value) => {
    setAnchors(
      anchors.map((a) => (a.id === id ? { ...a, glossary_guidance: value } : a))
    );
  };

  const saveGuidance = async (id) => {
    const anchor = anchors.find((a) => a.id === id);
    setSavingId(id);
    await apiFetch(`/memory/symbolic-anchors/${id}/`, {
      method: "PATCH",
      body: { glossary_guidance: anchor.glossary_guidance },
    });
    setSavingId(null);
  };

  return (
    <div className="container my-4">
      <h1 className="mb-3">Glossary Anchor Admin</h1>
      <ul className="list-group">
        {anchors.map((a) => (
          <li key={a.id} className="list-group-item">
            <strong>{a.label}</strong> ({a.slug})
            <textarea
              className="form-control mt-2"
              rows={2}
              value={a.glossary_guidance || ""}
              onChange={(e) => handleChange(a.id, e.target.value)}
            />
            <button
              className="btn btn-primary btn-sm mt-1"
              onClick={() => saveGuidance(a.id)}
              disabled={savingId === a.id}
            >
              {savingId === a.id ? "Saving..." : "Save"}
            </button>
          </li>
        ))}
        {anchors.length === 0 && (
          <li className="list-group-item text-muted">No anchors found.</li>
        )}
      </ul>
    </div>
  );
}
