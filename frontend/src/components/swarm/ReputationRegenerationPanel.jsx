import { useEffect, useState } from "react";
import { fetchReputationRebirths } from "../../api/agents";

export default function ReputationRegenerationPanel() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchReputationRebirths();
        setEvents(data.results || data);
      } catch (err) {
        console.error("Failed to load regeneration events", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Reputation Regeneration</h5>
      <ul className="list-group">
        {events.map((e) => (
          <li key={e.id} className="list-group-item">
            {e.assistant} – {e.regenerated_score}
          </li>
        ))}
        {events.length === 0 && (
          <li className="list-group-item text-muted">No regeneration events.</li>
        )}
      </ul>
    </div>
  );
}
