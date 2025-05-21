import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ArchetypeEvolutionPanel() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    apiFetch("/agents/swarm-memory/?origin=archetype_shift")
      .then(setEntries)
      .catch(() => setEntries([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Archetype Evolution</h5>
      <ul className="list-group">
        {entries.map((e) => (
          <li key={e.id} className="list-group-item">
            {e.title}
          </li>
        ))}
        {entries.length === 0 && (
          <li className="list-group-item text-muted">No evolution events.</li>
        )}
      </ul>
    </div>
  );
}
