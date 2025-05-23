import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualActionPanel() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    apiFetch("/simulation/ritual-launcher/")
      .then((res) => setEvents(res.results || res))
      .catch(() => setEvents([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Ritual Launcher</h5>
      <ul className="list-group">
        {events.map((e) => (
          <li key={e.id} className="list-group-item">
            {e.trigger_method} – {e.belief_impact_score}
          </li>
        ))}
        {events.length === 0 && (
          <li className="list-group-item text-muted">No rituals triggered.</li>
        )}
      </ul>
    </div>
  );
}
