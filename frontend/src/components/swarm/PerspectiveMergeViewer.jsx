import { useEffect, useState } from "react";
import { fetchPerspectiveMerges } from "../../api/agents";

export default function PerspectiveMergeViewer() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    fetchPerspectiveMerges()
      .then((d) => setEvents(d.results || d))
      .catch(() => setEvents([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Perspective Merges</h5>
      <ul className="list-group">
        {events.map((e) => (
          <li key={e.id} className="list-group-item">
            {e.topic}
          </li>
        ))}
        {events.length === 0 && (
          <li className="list-group-item text-muted">No merge events.</li>
        )}
      </ul>
    </div>
  );
}
