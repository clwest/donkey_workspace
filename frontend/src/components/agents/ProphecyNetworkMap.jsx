import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ProphecyNetworkMap() {
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    apiFetch("/assistants/prophecy-nodes/")
      .then(setNodes)
      .catch(() => setNodes([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Prophecy Network Map</h5>
      <ul className="list-group">
        {nodes.map((n) => (
          <li key={n.id} className="list-group-item">
            {n.forecast_window} – {n.predicted_events?.slice(0, 50)}
          </li>
        ))}
        {nodes.length === 0 && (
          <li className="list-group-item text-muted">No prophecy data.</li>
        )}
      </ul>
    </div>
  );
}
