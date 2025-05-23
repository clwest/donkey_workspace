import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MigrationGateConsole() {
  const [gates, setGates] = useState([]);

  useEffect(() => {
    apiFetch("/migration-gates/")
      .then((res) => setGates(res.results || res))
      .catch(() => setGates([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Archetype Migration Gates</h5>
      <ul className="list-group">
        {gates.map((g) => (
          <li key={g.id} className="list-group-item">
            <strong>{g.gate_name}</strong>
          </li>
        ))}
        {gates.length === 0 && (
          <li className="list-group-item text-muted">No gates defined.</li>
        )}
      </ul>
    </div>
  );
}
