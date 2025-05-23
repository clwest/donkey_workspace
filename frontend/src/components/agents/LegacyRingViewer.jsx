import { useEffect, useState } from "react";
import { fetchLegacyRings } from "../../api/agents";

export default function LegacyRingViewer() {
  const [rings, setRings] = useState([]);

  useEffect(() => {
    fetchLegacyRings().then(setRings).catch(() => setRings([]));
  }, []);

  if (rings.length === 0) return <div>No legacy rings.</div>;

  return (
    <div className="card">
      <div className="card-header">Legacy Rings</div>
      <ul className="list-group list-group-flush">
        {rings.map((r) => (
          <li key={r.id} className="list-group-item">
            <strong>{r.role_tag}</strong> – {new Date(r.timestamp).toLocaleDateString()}
          </li>
        ))}
      </ul>
    </div>
  );
}
