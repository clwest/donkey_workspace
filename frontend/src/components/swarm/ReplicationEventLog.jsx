import { useEffect, useState } from "react";
import { fetchKnowledgeReplications } from "../../api/agents";

export default function ReplicationEventLog() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchKnowledgeReplications();
        setEvents(data.results || data);
      } catch (err) {
        console.error("Failed to load replication events", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Knowledge Replication Events</h5>
      <ul className="list-group">
        {events.map((e) => (
          <li key={e.id} className="list-group-item">
            {e.transformed_summary}
          </li>
        ))}
        {events.length === 0 && (
          <li className="list-group-item text-muted">No events.</li>
        )}
      </ul>
    </div>
  );
}

