import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DirectiveMemoryBoard() {
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/directive-memory/");
        setNodes(res.results || res);
      } catch (err) {
        console.error("Failed to load directive memory", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Directive Memory Nodes</h5>
      <ul className="list-group">
        {nodes.map((n) => (
          <li key={n.id} className="list-group-item">
            <strong>{n.assistant_name || n.assistant}</strong> – {n.temporal_scope}
          </li>
        ))}
        {nodes.length === 0 && (
          <li className="list-group-item text-muted">No directive nodes.</li>
        )}
      </ul>
    </div>
  );
}
