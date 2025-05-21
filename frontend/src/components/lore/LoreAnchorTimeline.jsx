import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function LoreAnchorTimeline() {
  const [anchors, setAnchors] = useState([]);

  useEffect(() => {
    apiFetch("/agents/lore-anchors/")
      .then(setAnchors)
      .catch(() => setAnchors([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Lore Anchors</h5>
      <ul className="list-group">
        {anchors.map((a) => (
          <li key={a.id} className="list-group-item">
            <strong>{a.anchor_type}</strong> - {a.timestamp}
          </li>
        ))}
        {anchors.length === 0 && (
          <li className="list-group-item text-muted">No anchors found.</li>
        )}
      </ul>
    </div>
  );
}
