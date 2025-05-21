import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SceneMatchesPanel({ assistantSlug }) {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    if (!assistantSlug) return;
    apiFetch(`/storyboard/relevant/${assistantSlug}/`)
      .then((data) => setEvents(data || []))
      .catch((err) => console.error("Failed to load scene events", err));
  }, [assistantSlug]);

  if (!events.length) return null;

  return (
    <div className="card mb-3">
      <div className="card-header">Scene Matches</div>
      <ul className="list-group list-group-flush">
        {events.map((e) => (
          <li key={e.id} className="list-group-item">
            {e.title} {e.scene && <span className="text-muted">({e.scene})</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}
