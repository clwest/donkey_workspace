import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function BeliefContinuityDashboard() {
  const [rituals, setRituals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/belief-continuity/");
        setRituals(res.results || res);
        setLoading(false);
      } catch (err) {
        console.error("Failed to load continuity rituals", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Belief Continuity Rituals</h5>
      {loading && <div>Loading rituals...</div>}
      <ul className="list-group">
        {rituals.map((r) => (
          <li key={r.id} className="list-group-item">
            {r.outgoing_assistant} → {r.incoming_assistant} ({r.ritual_type})
          </li>
        ))}
        {rituals.length === 0 && (
          <li className="list-group-item text-muted">No rituals logged.</li>
        )}
      </ul>
    </div>
  );
}
