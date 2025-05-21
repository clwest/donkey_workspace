import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function NegotiationChamber() {
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/swarm/belief-negotiations/");
        setSessions(res.results || res);
      } catch (err) {
        console.error("Failed to load sessions", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Belief Negotiations</h5>
      <ul className="list-group">
        {sessions.map((s) => (
          <li key={s.id} className="list-group-item">
            <strong>{s.outcome}</strong> – {s.proposed_resolution || "pending"}
          </li>
        ))}
        {sessions.length === 0 && (
          <li className="list-group-item text-muted">No negotiation sessions.</li>
        )}
      </ul>
    </div>
  );
}
