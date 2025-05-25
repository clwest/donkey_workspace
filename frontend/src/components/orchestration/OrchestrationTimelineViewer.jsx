import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function OrchestrationTimelineViewer() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    apiFetch("/agents/orchestration/timeline/")
      .then((res) => setEvents(res))
      .catch(() => setEvents([]));
  }, []);

  return (
    <div className="my-4">
      <ul className="list-group">
        {events.map((e) => (
          <li key={e.id} className="list-group-item">
            {e.assistant_name} - {e.event_type} ({e.started_at})
          </li>
        ))}
        {events.length === 0 && (
          <li className="list-group-item text-muted">No events.</li>
        )}
      </ul>
    </div>
  );
}
