import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function DirectiveTrackerPanel({ assistantId }) {
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    if (!assistantId) return;
    async function load() {
      try {
        const res = await apiFetch(`/assistants/${assistantId}/directive-tracker/`);
        setNodes(res.results || res);
      } catch (err) {
        console.error("Failed to load directives", err);
        setNodes([]);
      }
    }
    load();
  }, [assistantId]);

  return (
    <div className="my-3">
      <h5>Directive Tracker</h5>
      <ul className="list-group">
        {nodes.map((n) => (
          <li key={n.id} className="list-group-item">
            {n.purpose_statement} — {n.progress || 0}%
          </li>
        ))}
        {nodes.length === 0 && (
          <li className="list-group-item text-muted">No directives.</li>
        )}
      </ul>
    </div>
  );
}
