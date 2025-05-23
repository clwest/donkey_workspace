import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualSimViewer() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/ritual-simulations/");
        setLogs(res.results || res);
      } catch (err) {
        console.error("Failed to load simulations", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Ritual Simulation Logs</h5>
      <ul className="list-group">
        {logs.map((l) => (
          <li key={l.id} className="list-group-item">
            {l.assistant} – {l.blueprint} ({l.symbolic_success_rate})
          </li>
        ))}
        {logs.length === 0 && (
          <li className="list-group-item text-muted">No simulations recorded.</li>
        )}
      </ul>
    </div>
  );
}
