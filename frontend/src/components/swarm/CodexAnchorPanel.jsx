import { useEffect, useState } from "react";
import { fetchCodexAnchors } from "../../api/agents";

export default function CodexAnchorPanel({ assistantId }) {
  const [anchors, setAnchors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!assistantId) return;
    fetchCodexAnchors(assistantId)
      .then((res) => {
        setAnchors(res.results || res);
        setError(null);
      })
      .catch((err) => {
        console.error("Failed to load codex anchors", err);
        setError("Awaiting Codex Guidance");
        setAnchors([]);
      })
      .finally(() => setLoading(false));
  }, [assistantId]);

  return (
    <div className="p-2 border rounded">
      <h5>Codex Anchors</h5>
      {loading && <div>Loading anchors...</div>}
      {error && !loading && (
        <div className="text-sm text-muted">{error}</div>
      )}
      <ul className="list-group">
        {anchors.map((a) => (
          <li key={a.id} className="list-group-item">
            {a.codex_title || a.codex} – strength {a.anchor_strength}
          </li>
        ))}
        {anchors.length === 0 && (
          <li className="list-group-item text-muted">No codex anchors.</li>
        )}
      </ul>
    </div>
  );
}
