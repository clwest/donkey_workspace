import { useEffect, useState } from "react";
import { fetchLearningReservoirs } from "../../api/agents";

export default function LearningReservoirViewer() {
  const [reservoirs, setReservoirs] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchLearningReservoirs();
        setReservoirs(data.results || data);
      } catch (err) {
        console.error("Failed to load reservoirs", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Learning Reservoirs</h5>
      <ul className="list-group">
        {reservoirs.map((r) => (
          <li key={r.id} className="list-group-item">
            {r.assistant} – {r.reservoir_status}
          </li>
        ))}
        {reservoirs.length === 0 && (
          <li className="list-group-item text-muted">No reservoirs.</li>
        )}
      </ul>
    </div>
  );
}

