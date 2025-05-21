import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DreamCultSimulator() {
  const [sims, setSims] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/swarm/dream-cults/");
        setSims(res.results || res);
      } catch (err) {
        console.error("Failed to load simulations", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Dream Cult Simulations</h5>
      <ul className="list-group">
        {sims.map((s) => (
          <li key={s.id} className="list-group-item">
            <strong>{s.linked_deity_name || s.linked_deity}</strong>
            <p className="mb-1 small">{s.ritual_patterns}</p>
          </li>
        ))}
        {sims.length === 0 && (
          <li className="list-group-item text-muted">No simulations running.</li>
        )}
      </ul>
    </div>
  );
}
