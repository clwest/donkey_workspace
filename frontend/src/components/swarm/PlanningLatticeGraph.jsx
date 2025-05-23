import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function PlanningLatticeGraph() {
  const [lattices, setLattices] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/planning-lattices/");
        setLattices(res.results || res);
      } catch (err) {
        console.error("Failed to load lattices", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Planning Lattices</h5>
      <ul className="list-group">
        {lattices.map((l) => (
          <li key={l.id} className="list-group-item">
            nodes: {Object.keys(l.role_nodes || {}).length}
          </li>
        ))}
        {lattices.length === 0 && (
          <li className="list-group-item text-muted">No lattices defined.</li>
        )}
      </ul>
    </div>
  );
}
