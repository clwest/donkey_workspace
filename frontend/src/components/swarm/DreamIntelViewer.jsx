import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DreamIntelViewer() {
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    apiFetch("/agents/dream-intel/")
      .then((data) => setNodes(data.results || data))
      .catch(() => setNodes([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Dream Intelligence</h5>
      <ul className="list-group">
        {nodes.map((n) => (
          <li key={n.id} className="list-group-item">
            {n.symbolic_payload}
          </li>
        ))}
        {nodes.length === 0 && (
          <li className="list-group-item text-muted">No dream intel found.</li>
        )}
      </ul>
    </div>
  );
}
