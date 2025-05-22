import { useEffect, useState } from "react";
import { fetchSymbolicSanctions } from "../../api/agents";

export default function SanctionTracker() {
  const [sanctions, setSanctions] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchSymbolicSanctions();
        setSanctions(data.results || data);
      } catch (err) {
        console.error("Failed to load sanctions", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Active Symbolic Sanctions</h5>
      <ul className="list-group">
        {sanctions.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.symbolic_penalty} ({s.duration_days} days)
          </li>
        ))}
        {sanctions.length === 0 && (
          <li className="list-group-item text-muted">No sanctions recorded.</li>
        )}
      </ul>
    </div>
  );
}
