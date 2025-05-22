import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function MythologyMeshViewer() {
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    apiFetch("/mythology-mesh/").then(setNodes);
  }, []);

  return (
    <div className="mb-3">
      <h5>Mythology Mesh</h5>
      <ul>
        {nodes.map((n) => (
          <li key={n.id}>{n.assistant} → {n.connected_to.join(", ")}</li>
        ))}
      </ul>
    </div>
  );
}
