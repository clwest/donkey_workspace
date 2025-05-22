import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function CycleBindingViewer() {
  const [bindings, setBindings] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/myth-cycles/");
        setBindings(res.results || res);
      } catch (err) {
        console.error("Failed to load myth cycles", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Myth Cycle Participation</h5>
      <ul className="list-group">
        {bindings.map((b) => (
          <li key={b.id} className="list-group-item">
            <strong>{b.assistant_name || b.assistant}</strong> – {b.cycle_name} ({b.cycle_phase})
          </li>
        ))}
        {bindings.length === 0 && (
          <li className="list-group-item text-muted">No cycle bindings recorded.</li>
        )}
      </ul>
    </div>
  );
}
