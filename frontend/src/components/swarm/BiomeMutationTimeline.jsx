import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function BiomeMutationTimeline() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/biome-mutations/");
        setEvents(res.results || res);
      } catch (err) {
        console.error("Failed to load mutation events", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Biome Mutation Timeline</h5>
      <ul className="list-group">
        {events.map((e) => (
          <li key={e.id} className="list-group-item">
            <strong>{e.trigger_type}</strong> - {e.mutation_summary}
          </li>
        ))}
        {events.length === 0 && (
          <li className="list-group-item text-muted">No mutations recorded.</li>
        )}
      </ul>
    </div>
  );
}
