import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SymbolicCoordinationPanel() {
  const [engines, setEngines] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/coordination-engine/");
        setEngines(res.results || res);
      } catch (err) {
        console.error("Failed to load coordination engines", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Coordination Engines</h5>
      <ul className="list-group">
        {engines.map((e) => (
          <li key={e.id} className="list-group-item">
            <strong>{e.guild}</strong> – {e.coordination_strategy}
          </li>
        ))}
        {engines.length === 0 && (
          <li className="list-group-item text-muted">No engines active.</li>
        )}
      </ul>
    </div>
  );
}
