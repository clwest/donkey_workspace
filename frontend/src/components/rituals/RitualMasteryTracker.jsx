import { useEffect, useState } from "react";
import { fetchRitualMastery } from "../../api/agents";

export default function RitualMasteryTracker() {
  const [records, setRecords] = useState([]);

  useEffect(() => {
    fetchRitualMastery()
      .then((d) => setRecords(d.results || d))
      .catch((e) => console.error("Failed to load ritual mastery", e));
  }, []);

  return (
    <div className="my-3">
      <h5>Ritual Mastery</h5>
      <ul className="list-group">
        {records.map((r) => (
          <li key={r.id} className="list-group-item">
            {r.symbolic_rank}
          </li>
        ))}
        {records.length === 0 && (
          <li className="list-group-item text-muted">No mastery records.</li>
        )}
      </ul>
    </div>
  );
}
