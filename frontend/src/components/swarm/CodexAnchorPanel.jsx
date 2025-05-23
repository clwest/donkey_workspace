import { useEffect, useState } from "react";
import { fetchCodexAnchors } from "../../api/agents";

export default function CodexAnchorPanel({ assistantId }) {
  const [anchors, setAnchors] = useState([]);

  useEffect(() => {
    if (!assistantId) return;
    fetchCodexAnchors(assistantId)
      .then((res) => setAnchors(res.results || res))
      .catch(() => setAnchors([]));
  }, [assistantId]);

  return (
    <div className="p-2 border rounded">
      <h5>Codex Anchors</h5>
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
