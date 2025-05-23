import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualVotingChamber() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    apiFetch("/ritual-votes/")
      .then((res) => setEvents(res.results || res))
      .catch(() => setEvents([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Ritual Votes</h5>
      <ul className="list-group">
        {events.map((e) => (
          <li key={e.id} className="list-group-item">
            {e.event_title} - {e.status}
          </li>
        ))}
        {events.length === 0 && (
          <li className="list-group-item text-muted">No active votes.</li>
        )}
      </ul>
    </div>
  );
}
