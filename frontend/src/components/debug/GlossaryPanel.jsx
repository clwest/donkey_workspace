import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import { renameGlossaryAnchor, deleteGlossaryAnchor } from "../../api/agents";

export default function GlossaryPanel() {
  const [logs, setLogs] = useState([]);
  const [anchors, setAnchors] = useState([]);

  const handleRemove = (slug) => {
    if (!window.confirm("Remove this anchor?")) return;
    deleteGlossaryAnchor(slug)
      .then(() => setAnchors((arr) => arr.filter((a) => a.slug !== slug)))
      .catch((err) => console.error("Delete failed", err));
  };

  const handleRename = (slug, current) => {
    const name = window.prompt("New label", current);
    if (!name) return;
    renameGlossaryAnchor(slug, name)
      .then((res) =>
        setAnchors((arr) => arr.map((a) => (a.slug === slug ? res : a)))
      )
      .catch((err) => console.error("Rename failed", err));
  };

  useEffect(() => {
    apiFetch("/memory/glossary-retries/")
      .then((res) => setLogs(res.results || []))
      .catch((err) => console.error("Failed to load glossary retries", err));
    apiFetch("/memory/symbolic-anchors/?show_empty=true")
      .then((res) => setAnchors(res.results || res))
      .catch((err) => console.error("Failed to load anchors", err));
  }, []);

  return (
    <div className="p-2 border rounded">
      <h5>Glossary Retry Logs</h5>
      {logs.length === 0 ? (
        <div className="text-muted">No retry logs</div>
      ) : (
        <ul className="small">
          {logs.map((log) => (
            <li key={log.id}>
              <strong>{log.anchor_label || log.anchor}</strong> – diff {log.score_diff}
            </li>
          ))}
        </ul>
      )}
      <h5 className="mt-3">Anchors</h5>
      {anchors.length === 0 ? (
        <div className="text-muted">No anchors</div>
      ) : (
        <ul className="small">
          {anchors.map((a) => (
            <li key={a.id} title={a.source === "inferred" ? "AI-inferred" : ""}>
              <strong>{a.label}</strong> ({a.slug}) – {a.chunks_count || 0}
              {a.retagged_count > 0 && (
                <span className="badge bg-info text-dark ms-1" title="Retagged chunks">
                  +{a.retagged_count}
                </span>
              )}
              {a.total_matches === 0 && (
                <span
                  className="badge bg-warning text-dark ms-1"
                  title="This anchor has no linked chunks or memory entries."
                >
                  0
                </span>
              )}
              {a.source === "inferred" && <span className="ms-1">🤖</span>}
              {a.total_matches === 0 && (
                <>
                  <button
                    className="btn btn-sm btn-link text-danger ms-1"
                    onClick={() => handleRemove(a.slug)}
                  >
                    🗑 Remove
                  </button>
                  <button
                    className="btn btn-sm btn-link ms-1"
                    onClick={() => handleRename(a.slug, a.label)}
                  >
                    ✏️ Rename
                  </button>
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

