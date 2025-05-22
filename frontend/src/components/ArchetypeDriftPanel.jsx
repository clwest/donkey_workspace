import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function ArchetypeDriftPanel() {
  const [forecasts, setForecasts] = useState([]);

  useEffect(() => {
    apiFetch("/archetype-drift/").then(setForecasts);
  }, []);

  return (
    <div className="mb-3">
      <h5>Archetype Drift</h5>
      <ul>
        {forecasts.map((f) => (
          <li key={f.id}>
            {f.assistant} → {f.predicted_archetype} ({f.drift_score})
          </li>
        ))}
      </ul>
    </div>
  );
}
