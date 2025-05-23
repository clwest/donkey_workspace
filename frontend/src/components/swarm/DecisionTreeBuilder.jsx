import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DecisionTreeBuilder() {
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    apiFetch("/simulation/decision-trees/")
      .then((res) => setNodes(res.results || res))
      .catch(() => setNodes([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Decision Trees</h5>
      <ul className="list-group">
        {nodes.map((n) => (
          <li key={n.id} className="list-group-item">
            {n.symbolic_condition}
          </li>
        ))}
        {nodes.length === 0 && (
          <li className="list-group-item text-muted">No decision nodes.</li>
        )}
      </ul>
    </div>
  );
}
