import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualForecastPanel() {
  const [rituals, setRituals] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch(`/swarm/ritual-forecast/`);
        setRituals(res);
      } catch (err) {
        console.error("Failed to load ritual forecast", err);
      }
    }
    load();
  }, []);

  if (!rituals.length) {
    return null;
  }

  return (
    <div>
      <h5 className="mb-2">Upcoming Rituals</h5>
      <ul className="list-group">
        {rituals.map((r, idx) => (
          <li key={idx} className="list-group-item">
            <strong>{r.title}</strong>
            <p className="mb-1 small">{r.details}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
