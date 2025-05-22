import { useEffect, useState } from "react";
import { fetchTreatyBreaches } from "../../api/agents";

export default function TreatyBreachRitualLog() {
  const [breaches, setBreaches] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchTreatyBreaches();
        setBreaches(data.results || data);
      } catch (err) {
        console.error("Failed to load treaty breaches", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Treaty Breach Rituals</h5>
      <ul className="list-group">
        {breaches.map((b) => (
          <li key={b.id} className="list-group-item">
            {b.triggered_ritual} – {b.breach_reason}
          </li>
        ))}
        {breaches.length === 0 && (
          <li className="list-group-item text-muted">No treaty breaches logged.</li>
        )}
      </ul>
    </div>
  );
}
