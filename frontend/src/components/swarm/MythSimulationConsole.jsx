import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythSimulationConsole() {
  const [sims, setSims] = useState([]);

  useEffect(() => {
    apiFetch("/simulation/simulators/")
      .then((res) => setSims(res.results || res))
      .catch(() => setSims([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Myth Simulators</h5>
      <ul className="list-group">
        {sims.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.simulation_title}
          </li>
        ))}
        {sims.length === 0 && (
          <li className="list-group-item text-muted">No simulators.</li>
        )}
      </ul>
    </div>
  );
}
