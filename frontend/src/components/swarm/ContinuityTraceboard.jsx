import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ContinuityTraceboard() {
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    apiFetch("/continuity-engine/")
      .then((res) => setNodes(res.results || res))
      .catch(() => setNodes([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Continuity Engine Nodes</h5>
      <ul className="list-group">
        {nodes.map((n) => (
          <li key={n.id} className="list-group-item">
            <strong>{n.linked_assistant}</strong>
          </li>
        ))}
        {nodes.length === 0 && (
          <li className="list-group-item text-muted">No nodes recorded.</li>
        )}
      </ul>
    </div>
  );
}
