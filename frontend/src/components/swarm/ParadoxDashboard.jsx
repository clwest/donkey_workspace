import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ParadoxDashboard() {
  const [attempts, setAttempts] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/swarm/paradox-resolution/");
        setAttempts(res.results || res);
      } catch (err) {
        console.error("Failed to load paradox attempts", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Paradox Resolution Attempts</h5>
      <ul className="list-group">
        {attempts.map((a) => (
          <li key={a.id} className="list-group-item">
            <strong>{a.attempted_by_name || a.attempted_by}</strong>: {a.logic_strategy}
          </li>
        ))}
        {attempts.length === 0 && (
          <li className="list-group-item text-muted">No paradox attempts logged.</li>
        )}
      </ul>
    </div>
  );
}
