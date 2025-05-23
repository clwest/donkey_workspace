import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function FusionConsole() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    apiFetch("/archetype-fusion/").then(setEvents);
  }, []);

  return (
    <div className="mb-3">
      <h5>Archetype Fusions</h5>
      <ul>
        {events.map((e) => (
          <li key={e.id}>
            {e.primary_archetype} + {e.merged_with} → {e.resulting_archetype}
          </li>
        ))}
      </ul>
    </div>
  );
}
